import os
from dotenv import load_dotenv

load_dotenv()
TRAIN = os.getenv("TRAIN")
LR = 3e-4
GAMMA = 0.99
E_BATCH_SIZE = 128
A_BATCH_SIZE = 128
BC_BATCH_SIZE = 128
TAU = 0.005        # 软更新系数
# IMG_DIM_X = 96
IMG_DIM_X = 64
# IMG_DIM_Y = 96
IMG_DIM_Y = 64
PATCH_SIZE = 16
IN_CHANNEL = 12
EMBED_DIM = 256
DEPTH = 2
HEADS = 4