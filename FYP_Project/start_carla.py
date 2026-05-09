import subprocess
import time

def restart_carla_docker(container_name="carla_server"):
    print(f"--- 正在重启 Docker 容器: {container_name} ---")
    try:
        # docker run --privileged --runtime nvidia --name carla-server --rm --net=host 
        # --gpus all carlasim/carla:0.9.15 ./CarlaUE4.sh -RenderOffScreen -nosound -quality-level=High 
        # -ResX=1 -ResY=1 -fps=5 -carla-port=2000
        # 1. 停止并移除现有容器（强制释放显存和端口）
        subprocess.run(["docker", "stop", container_name], check=False)
        subprocess.run(["docker", "rm", "-f", container_name], check=False)
        
        # 2. 重新启动容器
        # 注意：这里需要根据你的镜像版本和显卡配置修改参数
        docker_cmd = [
            "docker", "run", "-d", 
            "--privileged",
            "--name", container_name,
            "--gpus", "all",             # 使用 GPU
            "-p", "2000-2002:2000-2002", # 映射端口
            "--runtime=nvidia",
            "-e", "NVIDIA_VISIBLE_DEVICES=all",
            "carlasim/carla:0.9.15",     # 你的镜像名称
            "/bin/bash", "CarlaUE4.sh", 
            "-RenderOffScreen",                 # 必须添加：禁止渲染窗口
            "-nosound",                         # 建议添加：禁止音频，节省资源
            "-quality-level=Low", 
            "-vulkan"
        ]
        subprocess.run(docker_cmd, check=True)
        
        print("等待 CARLA 镜像初始化...")
        time.sleep(8)
    except Exception as e:
        print(f"Docker 重启失败: {e}")

if __name__ == "__main__":
    restart_carla_docker()