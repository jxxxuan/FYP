"""
FastAPI backend for Autonomous Driving Model Demo
Manages CARLA simulation sessions and model inference
"""
 
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import asyncio
import subprocess
import uuid
import json
import threading
import time
import os
import signal
from enum import Enum
 
app = FastAPI(title="AD Model Demo API")
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
# ── 状态管理 ──────────────────────────────────────────────────────────
class SessionStatus(str, Enum):
    IDLE = "idle"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"
 
class SessionState:
    def __init__(self):
        self.status: SessionStatus = SessionStatus.IDLE
        self.session_id: Optional[str] = None
        self.process: Optional[subprocess.Popen] = None
        self.logs: list[str] = []
        self.error: Optional[str] = None
        self.config: Optional[dict] = None
        self.lock = threading.Lock()
 
    def add_log(self, msg: str):
        timestamp = time.strftime("%H:%M:%S")
        self.logs.append(f"[{timestamp}] {msg}")
        if len(self.logs) > 200:
            self.logs.pop(0)
 
session = SessionState()
 
# ── 地图信息 ───────────────────────────────────────────────────────────
MAPS = {
    "Town03": {
        "name": "Town 03",
        "description": "中型城市，包含环形交叉路口、高速公路入口、隧道",
        "spawn_points": 265,
        "preview": "/maps/town03.jpg"
    },
    "Town04": {
        "name": "Town 04",
        "description": "小型城镇，含高速公路、郊区道路，适合高速场景",
        "spawn_points": 372,
        "preview": "/maps/town04.jpg"
    },
    "Town05": {
        "name": "Town 05",
        "description": "方格网络城市，多车道道路，适合复杂城市驾驶",
        "spawn_points": 302,
        "preview": "/maps/town05.jpg"
    }
}
 
# ── 请求模型 ──────────────────────────────────────────────────────────
class SimulationConfig(BaseModel):
    map: str
    spawn_point_index: int = 0
    num_vehicles: int = 20
    # 模型参数
    prediction_horizon: int = 50      # 预测步长
    confidence_threshold: float = 0.5  # 置信度阈值
    max_speed: float = 30.0           # 最大速度 km/h
    # 可选
    seed: int = 42
 
# ── API 路由 ──────────────────────────────────────────────────────────
 
@app.get("/api/maps")
async def get_maps():
    """获取支持的地图列表"""
    return {"maps": MAPS}
 
@app.get("/api/maps/{map_id}/spawn-points")
async def get_spawn_points(map_id: str):
    """获取地图的 spawn points（实际使用时从 CARLA 获取）"""
    if map_id not in MAPS:
        raise HTTPException(status_code=404, detail="地图不存在")
    # 实际项目中这里调用 CARLA client 获取真实 spawn points
    # 这里返回模拟数据
    count = MAPS[map_id]["spawn_points"]
    points = [
        {
            "index": i,
            "x": round((i * 17.3) % 400 - 200, 1),
            "y": round((i * 23.7) % 400 - 200, 1),
            "z": 0.0,
            "yaw": round((i * 37) % 360, 1)
        }
        for i in range(min(count, 50))  # 只返回前50个，实际可全部返回
    ]
    return {"spawn_points": points}
 
@app.get("/api/session/status")
async def get_status():
    """获取当前会话状态"""
    with session.lock:
        return {
            "status": session.status,
            "session_id": session.session_id,
            "config": session.config,
            "error": session.error,
            "log_count": len(session.logs)
        }
 
@app.post("/api/session/start")
async def start_session(config: SimulationConfig, background_tasks: BackgroundTasks):
    """启动仿真会话"""
    with session.lock:
        if session.status in (SessionStatus.STARTING, SessionStatus.RUNNING):
            raise HTTPException(status_code=400, detail="已有会话正在运行")
        if config.map not in MAPS:
            raise HTTPException(status_code=400, detail="不支持的地图")
 
        session.status = SessionStatus.STARTING
        session.session_id = str(uuid.uuid4())[:8]
        session.logs = []
        session.error = None
        session.config = config.dict()
 
    background_tasks.add_task(run_simulation, config)
    return {"session_id": session.session_id, "message": "仿真启动中..."}
 
@app.post("/api/session/stop")
async def stop_session():
    """停止当前会话"""
    with session.lock:
        if session.status not in (SessionStatus.STARTING, SessionStatus.RUNNING):
            raise HTTPException(status_code=400, detail="没有正在运行的会话")
        session.status = SessionStatus.STOPPING
 
    _kill_process()
    with session.lock:
        session.status = SessionStatus.IDLE
        session.process = None
        session.add_log("会话已手动停止")
 
    return {"message": "会话已停止"}
 
@app.get("/api/session/logs")
async def get_logs(since: int = 0):
    """获取日志（支持增量获取）"""
    with session.lock:
        logs = session.logs[since:]
        return {"logs": logs, "total": len(session.logs)}
 
@app.get("/api/session/logs/stream")
async def stream_logs():
    """SSE 实时推送日志"""
    async def event_generator():
        last_index = 0
        while True:
            with session.lock:
                new_logs = session.logs[last_index:]
                last_index = len(session.logs)
                status = session.status
 
            for log in new_logs:
                yield f"data: {json.dumps({'log': log, 'status': status})}\n\n"
 
            if status in (SessionStatus.IDLE, SessionStatus.ERROR):
                yield f"data: {json.dumps({'done': True, 'status': status})}\n\n"
                break
 
            await asyncio.sleep(0.3)
 
    return StreamingResponse(event_generator(), media_type="text/event-stream")
 
# ── 仿真运行逻辑 ──────────────────────────────────────────────────────
 
def _kill_process():
    """终止仿真进程"""
    with session.lock:
        proc = session.process
    if proc and proc.poll() is None:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except Exception:
            proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
 
def run_simulation(config: SimulationConfig):
    """在后台线程中运行仿真脚本"""
    session.add_log(f"初始化仿真环境: {config.map}")
    session.add_log(f"车辆数量: {config.num_vehicles}, Spawn Point: #{config.spawn_point_index}")
    session.add_log(f"模型参数 — 预测步长: {config.prediction_horizon}, 置信度: {config.confidence_threshold}")
 
    # 构建命令行参数，调用你的推理脚本
    script_path = os.path.join(os.path.dirname(__file__), "inference_runner.py")
    cmd = [
        "python3", script_path,
        "--map", config.map,
        "--spawn-point", str(config.spawn_point_index),
        "--num-vehicles", str(config.num_vehicles),
        "--prediction-horizon", str(config.prediction_horizon),
        "--confidence-threshold", str(config.confidence_threshold),
        "--max-speed", str(config.max_speed),
        "--seed", str(config.seed),
    ]
 
    try:
        session.add_log("正在连接 CARLA 服务器...")
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            preexec_fn=os.setsid
        )
        with session.lock:
            session.process = proc
            session.status = SessionStatus.RUNNING
 
        session.add_log("✓ 仿真已启动，模型推理进行中...")
 
        # 实时读取输出日志
        for line in proc.stdout:
            line = line.rstrip()
            if line:
                session.add_log(line)
            with session.lock:
                if session.status == SessionStatus.STOPPING:
                    break
 
        proc.wait()
 
        with session.lock:
            if session.status != SessionStatus.STOPPING:
                if proc.returncode == 0:
                    session.status = SessionStatus.IDLE
                    session.add_log("✓ 仿真正常结束")
                else:
                    session.status = SessionStatus.ERROR
                    session.error = f"进程退出码: {proc.returncode}"
                    session.add_log(f"✗ 仿真异常退出 (code {proc.returncode})")
 
    except FileNotFoundError:
        with session.lock:
            session.status = SessionStatus.ERROR
            session.error = "找不到推理脚本 inference_runner.py"
            session.add_log("✗ 错误: 找不到推理脚本")
    except Exception as e:
        with session.lock:
            session.status = SessionStatus.ERROR
            session.error = str(e)
            session.add_log(f"✗ 错误: {e}")
    finally:
        with session.lock:
            if session.status == SessionStatus.STOPPING:
                session.status = SessionStatus.IDLE
 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)