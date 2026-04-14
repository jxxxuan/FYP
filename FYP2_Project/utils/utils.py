import torch
from models.vit import ViTEncoder
from dotenv import load_dotenv
import os
import time
from hyperparameter import *
from constants import *
import glob
import re

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

def save_checkpoint(actor, actor_opt, critic, critic_opt, episode, total_updates):
    if not os.path.exists(CP_DIR):
        os.makedirs(CP_DIR)
    
    # 构造保存文件名
    timestamp = time.strftime("%m%d-%H%M")
    filename = os.path.join(CP_DIR, f"sac_carla_ep{episode}_{timestamp}.pth")
    
    torch.save({
        'episode': episode,
        'total_updates': total_updates,
        'actor_state_dict': actor.state_dict(),
        'critic_state_dict': critic.state_dict(),
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