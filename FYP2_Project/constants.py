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
IMG_DIM = 128
FIXED_DELTA_SECONDS = 0.05