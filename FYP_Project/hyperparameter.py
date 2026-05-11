import os
from dotenv import load_dotenv

load_dotenv()
TRAIN = os.getenv("TRAIN")
LR = 3e-4
GAMMA = 0.99
E_BATCH_SIZE = 32
A_BATCH_SIZE = 32
BC_BATCH_SIZE = 64
TAU = 0.005        # 软更新系数
IMG_DIM_X = 84
IMG_DIM_Y = 70
PATCH_SIZE = 16
IN_CHANNEL = 12
EMBED_DIM = 256
DEPTH = 2
HEADS = 4