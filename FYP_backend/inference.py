"""
inference_runner.py
被 FastAPI 后端调用的推理脚本
请在此处集成你的模型推理逻辑
"""
 
import argparse
import carla
import math
import time
import sys
import os
 
# 把 carla_painter.py 所在目录加入路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../examples"))
from carla_painter import CarlaPainter
 
# ── 在这里 import 你的模型 ──────────────────────────────────────────
# import torch
# from your_model import YourModel
 
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--map", default="Town03")
    parser.add_argument("--spawn-point", type=int, default=0)
    parser.add_argument("--num-vehicles", type=int, default=20)
    parser.add_argument("--prediction-horizon", type=int, default=50)
    parser.add_argument("--confidence-threshold", type=float, default=0.5)
    parser.add_argument("--max-speed", type=float, default=30.0)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()
 
def main():
    args = parse_args()
    print(f"[Runner] 启动场景: {args.map}, spawn={args.spawn_point}", flush=True)
 
    # ── 初始化 Painter ───────────────────────────────────────────────
    painter = CarlaPainter('localhost', 8089)
 
    # ── 连接 CARLA ───────────────────────────────────────────────────
    client = carla.Client('localhost', 2000)
    client.set_timeout(15.0)
    print(f"[Runner] 连接 CARLA...", flush=True)
 
    world = client.load_world(args.map)
    print(f"[Runner] ✓ 地图 {args.map} 加载完成", flush=True)
 
    previous_settings = world.get_settings()
    world.apply_settings(carla.WorldSettings(
        synchronous_mode=True,
        fixed_delta_seconds=1.0 / 30.0))
 
    # ── 生成 ego 车辆 ─────────────────────────────────────────────────
    spawn_points = world.get_map().get_spawn_points()
    if args.spawn_point >= len(spawn_points):
        print(f"[Runner] spawn point {args.spawn_point} 超出范围，使用 0", flush=True)
        args.spawn_point = 0
 
    blueprints = world.get_blueprint_library().filter("vehicle.*")
    blueprints = [x for x in blueprints if int(x.get_attribute('number_of_wheels')) == 4]
    blueprints[0].set_attribute('role_name', 'ego')
 
    ego_transform = spawn_points[args.spawn_point]
    results = client.apply_batch_sync(
        [carla.command.SpawnActor(blueprints[0], ego_transform)],
        True)
 
    if results[0].error:
        print(f"[Runner] ✗ 无法生成 ego 车辆: {results[0].error}", flush=True)
        return 1
 
    ego_vehicle = world.get_actor(results[0].actor_id)
    print(f"[Runner] ✓ ego 车辆已生成 (id={ego_vehicle.id})", flush=True)
 
    # ── 生成其他车辆 ──────────────────────────────────────────────────
    other_vehicles = []
    batch = []
    import random
    random.seed(args.seed)
    selected_spawns = random.sample(
        [p for i, p in enumerate(spawn_points) if i != args.spawn_point],
        min(args.num_vehicles, len(spawn_points) - 1)
    )
    for i, transform in enumerate(selected_spawns):
        bp = blueprints[(i + 1) % len(blueprints)]
        batch.append(
            carla.command.SpawnActor(bp, transform)
                .then(carla.command.SetAutopilot(carla.command.FutureActor, True))
        )
 
    results = client.apply_batch_sync(batch, True)
    for r in results:
        if not r.error:
            other_vehicles.append(r.actor_id)
    print(f"[Runner] ✓ 生成 {len(other_vehicles)} 辆其他车辆", flush=True)
 
    # ── 加载你的模型 ──────────────────────────────────────────────────
    # model = YourModel.load_from_checkpoint("your_model.ckpt")
    # model.eval()
    print(f"[Runner] ✓ 模型加载完成 (horizon={args.prediction_horizon}, threshold={args.confidence_threshold})", flush=True)
 
    # ── 主循环 ────────────────────────────────────────────────────────
    trajectory = []
    frame = 0
    print("[Runner] 开始推理循环...", flush=True)
 
    try:
        while True:
            world.tick()
            frame += 1
 
            loc = ego_vehicle.get_location()
            x, y, z = loc.x, -loc.y, loc.z  # CarlaViz y轴取反
 
            # 记录轨迹
            trajectory.append((x, y, z + 0.3))
            if len(trajectory) > 200:
                trajectory.pop(0)
 
            # ── 在这里调用你的模型推理 ──────────────────────────────
            # sensor_data = get_sensor_data(...)
            # predictions = model.predict(sensor_data, horizon=args.prediction_horizon)
            # confidence = predictions.confidence
            # predicted_path = predictions.waypoints  # list of (x, y, z)
 
            # ── 示例：用简单逻辑模拟预测轨迹 ──────────────────────
            yaw_rad = math.radians(ego_vehicle.get_transform().rotation.yaw)
            predicted_path = [
                (x + math.cos(yaw_rad) * i * 1.0,
                 y - math.sin(yaw_rad) * i * 1.0,
                 z + 0.5)
                for i in range(1, args.prediction_horizon // 5 + 1)
            ]
 
            # ── 每帧绘制 ──────────────────────────────────────────
            if frame % 2 == 0 and len(trajectory) >= 2:
                # 历史轨迹（红色，在 metadata 中定义）
                painter.draw_polylines([trajectory])
 
                # 预测路径（显示为点）
                if predicted_path:
                    painter.draw_points(predicted_path)
 
                # 朝向箭头
                arrow_end = (
                    x + math.cos(yaw_rad) * 4.0,
                    y - math.sin(yaw_rad) * 4.0,
                    z + 1.0
                )
                painter.draw_arrows([(x, y, z + 1.0)], [arrow_end])
 
                # 速度 + 推理信息
                vel = ego_vehicle.get_velocity()
                speed = 3.6 * math.sqrt(vel.x**2 + vel.y**2 + vel.z**2)
                painter.draw_texts(
                    [f"Speed: {speed:.1f} km/h",
                     f"Horizon: {args.prediction_horizon} steps"],
                    [(x, y, z + 5.0), (x, y, z + 6.5)]
                )
 
            if frame % 150 == 0:
                vel = ego_vehicle.get_velocity()
                speed = 3.6 * math.sqrt(vel.x**2 + vel.y**2 + vel.z**2)
                print(f"[Runner] frame={frame} speed={speed:.1f}km/h traj_len={len(trajectory)}", flush=True)
 
            time.sleep(0.01)
 
    except KeyboardInterrupt:
        print("[Runner] 收到中断信号，停止", flush=True)
 
    finally:
        world.apply_settings(previous_settings)
        ego_vehicle.destroy()
        if other_vehicles:
            client.apply_batch([carla.command.DestroyActor(x) for x in other_vehicles])
        painter.close()
        print("[Runner] ✓ 清理完成", flush=True)
 
    return 0
 
if __name__ == "__main__":
    sys.exit(main())