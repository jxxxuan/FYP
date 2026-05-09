#!/bin/bash

# --- 配置区 ---
PYTHON_SCRIPT="train.py"
CONDA_ENV="fyp"
CONTAINER_NAME="carla_server"
LOG_FILE="auto_restart.log"

echo "--- 监控脚本已启动 ---" | tee -a $LOG_FILE

while true
do
    # 检查 Python 进程是否还在 (使用 pgrep 更精准)
    if pgrep -f "$PYTHON_SCRIPT" > /dev/null
    then
        # Python 还在跑，不做任何事，静静等待
        sleep 30
    else
        # 发现 Python 停了（崩溃或自然结束）
        echo "$(date): 检测到 $PYTHON_SCRIPT 已停止，准备重启流程..." | tee -a $LOG_FILE

        # 1. 彻底清理环境 (只在重启时执行，确保下一次启动成功)
        echo "清理旧容器和端口..."
        sudo docker rm -f $CONTAINER_NAME > /dev/null 2>&1
        sudo fuser -k 2000/tcp > /dev/null 2>&1
        sudo fuser -k 8000/tcp > /dev/null 2>&1
        
        # 2. 重新启动 CARLA Docker
        # 这里建议使用普通 Town03 避开 Opt 地图的同步 Bug
        echo "重启 CARLA Server..."
        sudo docker run -d \
          --name $CONTAINER_NAME \
          --gpus all \
          --runtime=nvidia \
          --net=host \
          -e SDL_VIDEODRIVER=offscreen \
          carlasim/carla:0.9.15 \
          /bin/bash CarlaUE4.sh -RenderOffScreen -nosound -quality-level=Low -vulkan
        
        # 3. 等待 CARLA 启动就绪
        echo "等待 20 秒让 CARLA 稳定..."
        sleep 20

        # 4. 重新启动训练脚本
        echo "重启训练任务..."
        # 使用 conda run 确保环境正确，并把日志存下来方便你查错
        conda run -n $CONDA_ENV python $PYTHON_SCRIPT >> train_output.log 2>&1 &
        
        echo "已重新拉起训练进程，继续监控..." | tee -a $LOG_FILE
        sleep 60 # 给 Python 一分钟启动时间，防止高频重复重启
    fi
done