import subprocess
import time
import carla
from constants import *

def wait_for_carla(timeout=120, interval=5):
    """Actively probe if CARLA is ready"""
    deadline = time.time() + timeout
    attempt = 0
    while time.time() < deadline:
        attempt += 1
        try:
            client = carla.Client(CARLA_HOST, CARLA_PORT)
            client.set_timeout(30.0)
            # get_world() requires UE4 scene to be fully ready before returning
            # get_server_version() only requires the RPC service to be up, which is too early
            world = client.get_world()
            world.get_map()  # Double check that the map is also loaded
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
            "--rm",
            "--net=host",
            "--gpus", "all",  
            "carlasim/carla:0.9.15",     # Your image name
            "./CarlaUE4.sh", 
            "-RenderOffScreen", "-nosound",# Recommended: disable audio to save resources
            "-quality-level=High", 
            "-ResX=1", "-ResY=1", "-fps=5",
        ]
        subprocess.run(docker_cmd, check=True)

        wait_for_carla(timeout=120,interval=30)
    except Exception as e:
        print(f"Docker restart failed: {e}")

def stop_carla():
    subprocess.run(["docker", "stop", "carla-server"], check=False)
    subprocess.run(["docker", "rm", "-f", "carla-server"], check=False)

def restart_carla():
    print(f"--- Restarting Docker container: carla-server ---")
    # 1. Stop and remove existing container (force release of VRAM and ports)
    stop_carla()
    start_carla()
        
if __name__ == "__main__":
    restart_carla()