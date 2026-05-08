#!/bin/bash
while true; do
    echo "Starting Training Session..."
    python train.py  # 替换成你的文件名
    if [ $? -eq 0 ]; then
        echo "Training Finished Successfully."
        break
    else
        echo "Training crashed with exit code $?. Respawning in 10s..."
        # 可选：在这里加上重启 CARLA 服务端的命令
        sleep 10
    fi
done