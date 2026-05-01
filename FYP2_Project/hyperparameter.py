import os
from dotenv import load_dotenv

load_dotenv()
TRAIN = os.getenv("TRAIN")
LR = 3e-4
GAMMA = 0.99
E_BATCH_SIZE = 512
A_BATCH_SIZE = 512
BC_BATCH_SIZE = 256
TAU = 0.005        # 软更新系数
NUM_NPC = 40
# IMG_DIM_X = 96
IMG_DIM_X = 84
# IMG_DIM_Y = 96
IMG_DIM_Y = 84
PATCH_SIZE = 16
IN_CHANNEL = 12
EMBED_DIM = 256
DEPTH = 2
HEADS = 4
