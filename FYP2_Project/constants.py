import os
from dotenv import load_dotenv
import sys
from pathlib import Path

load_dotenv()

current_file = Path(__file__).resolve()
PROJECT_ROOT = current_file.parent
CARLA_PATH = PROJECT_ROOT / "CARLA" / "PythonAPI" / "carla"
CARLA_UTIL = PROJECT_ROOT / "CARLA" / "PythonAPI" / "util"
if CARLA_PATH.exists() and CARLA_UTIL.exists():
    sys.path.append(str(CARLA_PATH))
    sys.path.append(str(CARLA_UTIL))
else:
    print("--- 警告：未在项目内找到 CARLA 文件夹，请检查位置 ---")

CARLA_HOST = os.getenv("CARLA_HOST")
DRIVE_PATH = os.getenv("DRIVE_PATH")
DEBUG_IMG_DIM_X = 1080
DEBUG_IMG_DIM_Y = 480
FIXED_DELTA_SECONDS = 0.05
CHECK_POINT_INTERVAL = 5
UPDATE_PER_STEP = 5
ED_DIR = os.path.join(DRIVE_PATH, "expert_data","without_npc")
ED_N_DIR = os.path.join(DRIVE_PATH, "expert_data","with_npc")
CP_DIR = os.path.join(DRIVE_PATH, "checkpoints")
LOG_DIR = os.path.join(DRIVE_PATH, "logs")
TRAIN_JSON = os.path.join(DRIVE_PATH, "train_tasks.json")
TEST_JSON = os.path.join(DRIVE_PATH, "test_tasks.json")