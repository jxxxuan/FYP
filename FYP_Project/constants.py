import os
from dotenv import load_dotenv
import sys
from pathlib import Path
import torch

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
CARLA_PORT = os.getenv("CARLA_PORT")
DRIVE_PATH = os.getenv("DRIVE_PATH")
DEBUG_IMG_DIM_X = 1080
DEBUG_IMG_DIM_Y = 480
FPS = 5
FIXED_DELTA_SECONDS = 1.0 / FPS
SUBSTEP_DELTA = 0.0125
MAX_SUBSTEPS = 16
GRP = 1
CHECK_POINT_INTERVAL = 200
UPDATE_PER_STEP = 1
ED_DIR = os.path.join(DRIVE_PATH, "expert_data")
AG_DIR = os.path.join(DRIVE_PATH, "agent_data")
CP_DIR = os.path.join(DRIVE_PATH, "checkpoints")
RC_DIR = os.path.join(DRIVE_PATH, "record")
LOG_DIR = os.path.join(DRIVE_PATH, "logs")
TRAIN_LOG_DIR = os.path.join(DRIVE_PATH, "logs" ,"train_log.csv")
TRAIN_GRAPH_DIR = os.path.join(DRIVE_PATH, "logs" ,"train_graph.png")
TEST_LOG_DIR = os.path.join(DRIVE_PATH, "logs" ,"test_log.csv")
TEST_GRAPH_DIR = os.path.join(DRIVE_PATH, "logs" ,"test_graph.png")
DETAIL_LOG_DIR = os.path.join(DRIVE_PATH, "logs" ,"detail_log.csv")
DETAIL_GRAPH_DIR = os.path.join(DRIVE_PATH, "logs" ,"detail_graph.png")
TRAIN_JSON = os.path.join(DRIVE_PATH, "train_tasks.json")
TEST_JSON = os.path.join(DRIVE_PATH, "test_tasks.json")
INTESECTION_JSON = os.path.join(DRIVE_PATH, "intersections.json")
MAX_STEPS = 500
MAX_EPISODES = 200000
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
SENDER_EMAIL_PASSWORD = os.getenv("SENDER_EMAIL_PASSWORD")
PRETICK_STEP = 20
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
ACTION_DIM = 2
NUM_CAM = 3