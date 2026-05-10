import subprocess
import time
import carla
from constants import *

def wait_for_carla(timeout=120, interval=5):
    """主动探测 CARLA 是否就绪"""
    deadline = time.time() + timeout
    attempt = 0
    while time.time() < deadline:
        attempt += 1
        try:
            client = carla.Client(CARLA_HOST, CARLA_PORT)
            client.set_timeout(8.0)
            # get_world() 需要 UE4 场景完全就绪才会返回
            # get_server_version() 只需要 RPC 服务起来就行，太早了
            world = client.get_world()
            world.get_map()  # 再确认地图也加载好了
            print(f"CARLA ready (attempt {attempt})")
            return True
        except Exception:
            print(f"Waiting for CARLA... attempt {attempt}")
            time.sleep(interval)
    raise RuntimeError(f"CARLA did not start within {timeout}s")

def start_carla():
    # docker run --privileged --runtime nvidia --name carla-server --rm --net=host --gpus all 
    # carlasim/carla:0.9.15 ./CarlaUE4.sh -RenderOffScreen -nosound -quality-level=High -ResX=1 -ResY=1 -fps=5 
    # -carla-port=2000
    try:
        docker_cmd = [
            "docker", "run", "-d", 
            "--privileged",
            "--runtime","nvidia",
            "--name", "carla-server",
            "--net=host",
            "--gpus", "all",  
            "carlasim/carla:0.9.15",     # 你的镜像名称
            "./CarlaUE4.sh", 
            "-RenderOffScreen", "-nosound",# 建议添加：禁止音频，节省资源
            "-quality-level=High", 
            "-ResX=1", "-ResY=1", "-fps=5",
        ]
        subprocess.run(docker_cmd, check=True)

        wait_for_carla(host=CARLA_HOST, port=CARLA_PORT, timeout=120)
    except Exception as e:
        print(f"Docker 重启失败: {e}")

def restart_carla():
    print(f"--- 正在重启 Docker 容器: {"carla-server"} ---")
        
    # 1. 停止并移除现有容器（强制释放显存和端口）
    subprocess.run(["docker", "stop", "carla-server"], check=False)
    subprocess.run(["docker", "rm", "-f", "carla-server"], check=False)
    
    start_carla()
        
if __name__ == "__main__":
    restart_carla()