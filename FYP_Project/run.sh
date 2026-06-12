#!/bin/bash

# --- Configuration ---
PYTHON_SCRIPT="train.py"
CONDA_ENV="fyp"
CONTAINER_NAME="carla_server"
LOG_FILE="auto_restart.log"

echo "--- Monitor script started ---" | tee -a $LOG_FILE

while true
do
    # Check if Python process is still running (use pgrep for precision)
    if pgrep -f "$PYTHON_SCRIPT" > /dev/null
    then
        # Python is still running, do nothing, just wait
        sleep 30
    else
        # Python stopped (crashed or finished naturally)
        echo "$(date): Detected $PYTHON_SCRIPT stopped, preparing restart..." | tee -a $LOG_FILE

        # 1. Completely clean the environment (only run during restart, to ensure successful start next time)
        echo "Cleaning up old containers and ports..."
        sudo docker rm -f $CONTAINER_NAME > /dev/null 2>&1
        sudo fuser -k 2000/tcp > /dev/null 2>&1
        sudo fuser -k 8000/tcp > /dev/null 2>&1
        
        # 2. Restart CARLA Docker
        # Recommended to use regular Town03 to avoid the synchronization bug of the Opt map
        echo "Restarting CARLA Server..."
        sudo docker run -d \
          --name $CONTAINER_NAME \
          --gpus all \
          --runtime=nvidia \
          --net=host \
          -e SDL_VIDEODRIVER=offscreen \
          carlasim/carla:0.9.15 \
          /bin/bash CarlaUE4.sh -RenderOffScreen -nosound -quality-level=Low -vulkan
        
        # 3. Wait for CARLA to start and become ready
        echo "Waiting 20 seconds for CARLA to stabilize..."
        sleep 20

        # 4. Restart training script
        echo "Restarting training task..."
        # Use conda run to ensure correct environment and log outputs for debugging
        conda run -n $CONDA_ENV python $PYTHON_SCRIPT >> train_output.log 2>&1 &
        
        echo "Training process restarted, continuing monitoring..." | tee -a $LOG_FILE
        sleep 60 # Give Python 1 minute to start, to prevent high frequency repeating restarts
    fi
done