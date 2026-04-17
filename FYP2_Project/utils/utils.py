import torch
from dotenv import load_dotenv
import os
import time
import glob
import re
import sys
import carla
from models.sac_agent import Actor, DoubleCritic
import torch.optim as optim

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from models.vit import ViTEncoder
from hyperparameter import *
from constants import *

def create_vit():
    return ViTEncoder(
        img_size_h=IMG_DIM_Y, 
        img_size_w=IMG_DIM_X*2, 
        patch_size=16, 
        in_chans=12,
        embed_dim=256, 
        depth=2, 
        num_heads=1
    )

def create_model(action_dim, device):
    vit_encoder_a = create_vit()

    # 2. Critic 的视觉编码器 (用于 Double Q)
    shared_vit_c1 = create_vit()
    shared_vit_c2 = create_vit()

    # 3. Target Critic 的视觉编码器 (用于稳定训练) [cite: 227]
    shared_vit_tc1 = create_vit()
    shared_vit_tc2 = create_vit()

    actor = Actor(vit_encoder_a, action_dim).to(device)
    
    critic = DoubleCritic(shared_vit_c1, shared_vit_c2, action_dim).to(device)
    target_critic = DoubleCritic(shared_vit_tc1, shared_vit_tc2, action_dim).to(device)

    actor_opt = optim.Adam(actor.parameters(), lr=LR)
    critic_opt = optim.Adam(critic.parameters(), lr=LR)

    return actor, critic, target_critic, actor_opt, critic_opt

def save_checkpoint(actor, actor_opt, critic, critic_opt, episode, total_updates):
    if not os.path.exists(CP_DIR):
        os.makedirs(CP_DIR)
    
    # 构造保存文件名
    timestamp = time.strftime("%m%d-%H%M")
    filename = os.path.join(CP_DIR, f"sac_carla_ep{episode}_{timestamp}.pth")
    
    raw_actor = actor._orig_mod if hasattr(actor, "_orig_mod") else actor
    raw_critic = critic._orig_mod if hasattr(critic, "_orig_mod") else critic

    torch.save({
        'episode': episode,
        'total_updates': total_updates,
        'actor_state_dict': raw_actor.state_dict(),
        'critic_state_dict': raw_critic.state_dict(),
        'actor_opt_state_dict': actor_opt.state_dict(), # 增加这一行
        'critic_opt_state_dict': critic_opt.state_dict(), # 增加这一行
    }, filename)
    print(f"\n[SUCCESS] Saved to: {filename}")

def load_latest_checkpoint(actor, actor_opt, critic, critic_opt, target_critic, device):
    if not os.path.exists(CP_DIR):
        print(f"--- dir {CP_DIR} not exist ---")
        return 0
    
    # 1. 获取文件夹下所有 .pth 文件
    ckpt_files = glob.glob(os.path.join(CP_DIR, "*.pth"))
    
    if not ckpt_files:
        print("--- No Checkpoint file ---")
        return 0, 0

    # 2. 定义一个辅助函数，提取文件名里的 episode 数字
    # 假设你的文件名格式是 sac_carla_ep150_...
    def extract_episode(filename):
        match = re.search(r'ep(\d+)', filename)
        return int(match.group(1)) if match else -1

    # 3. 找到 episode 最大的那个文件
    latest_ckpt = max(ckpt_files, key=extract_episode)
    max_ep = extract_episode(latest_ckpt)

    if max_ep == -1:
        print("--- 文件名格式不匹配（未找到 'ep' 数字），请检查文件名 ---")
        return 0, 0

    # 4. 执行加载逻辑
    print(f"--- Latest Checkpoint: {latest_ckpt}---")
    checkpoint = torch.load(latest_ckpt, map_location=device)
    
    actor.load_state_dict(checkpoint['actor_state_dict'])
    actor_opt.load_state_dict(checkpoint['actor_opt_state_dict'])
    critic.load_state_dict(checkpoint['critic_state_dict'])
    critic_opt.load_state_dict(checkpoint['critic_opt_state_dict'])
    target_critic.load_state_dict(critic.state_dict())
    
    return checkpoint['episode'] + 1, checkpoint.get('total_updates', 0)

def build_pose(task):
    s = task['start_pose']
    t = task['target_pose']
    
    start = carla.Transform(
        carla.Location(x=s['x'], y=s['y'], z=s['z']),
        carla.Rotation(yaw=s['rotate'])
    )
    target = carla.Location(x=t['x'], y=t['y'], z=t['z'])
    
    return start, target