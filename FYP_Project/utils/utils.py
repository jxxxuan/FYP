import json
import random

import torch
from dotenv import load_dotenv
import os
import time
import glob
import re
import sys
import carla
import torch.optim as optim
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from models.vit import ViTEncoder
from hyperparameter import *
from constants import *
from models.sac_agent import Actor, DoubleCritic

def create_vit():
    return ViTEncoder(
        img_size_h=IMG_DIM_Y, 
        img_size_w=IMG_DIM_X*2, 
        patch_size=PATCH_SIZE, 
        in_chans=IN_CHANNEL,
        embed_dim=EMBED_DIM, 
        depth=DEPTH, 
        num_heads=HEADS
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

def save_checkpoint(actor, actor_opt, critic, critic_opt, alpha_opt, log_alpha, episode, total_updates):
    if not os.path.exists(CP_DIR):
        os.makedirs(CP_DIR)
    
    timestamp = time.strftime("%m%d-%H%M")
    filename = os.path.join(CP_DIR, f"ep{episode}_{timestamp}.pth")
    
    raw_actor = actor._orig_mod if hasattr(actor, "_orig_mod") else actor
    raw_critic = critic._orig_mod if hasattr(critic, "_orig_mod") else critic

    torch.save({
        'episode': episode,
        'total_updates': total_updates,
        'actor_state_dict': raw_actor.state_dict(),
        'critic_state_dict': raw_critic.state_dict(),
        # 'actor_state_dict': actor.state_dict(),
        # 'critic_state_dict': critic.state_dict(),
        'actor_opt_state_dict': actor_opt.state_dict(),
        'critic_opt_state_dict': critic_opt.state_dict(),
        'log_alpha_opt': log_alpha,           # 必须保存这个张量
        'alpha_opt_state_dict': alpha_opt.state_dict(), # 必须保存它的优化器
    }, filename)
    print(f"\n[SUCCESS] Saved to: {filename}")

def save_best_actor(actor, actor_opt, id):
    if not os.path.exists(CP_DIR):
        os.makedirs(CP_DIR)
    
    timestamp = time.strftime("%m%d-%H%M")
    filename = os.path.join(CP_DIR, f"best_actor_id{id}.pth")
    
    raw_actor = actor._orig_mod if hasattr(actor, "_orig_mod") else actor

    torch.save({
        'actor_state_dict': raw_actor.state_dict(),
        # 'actor_state_dict': actor.state_dict(),
        # 'critic_state_dict': critic.state_dict(),
        'actor_opt_state_dict': actor_opt.state_dict(),
    }, filename)
    print(f"\n[SUCCESS] Saved to: {filename}")

def load_latest_checkpoint(device):
    # 1. 获取文件夹下所有 .pth 文件
    ckpt_files = glob.glob(os.path.join(CP_DIR, "*.pth"))
    
    if not ckpt_files:
        print("--- No Checkpoint file ---")
        models = dict()
        models['actor'], models['critic'], models['target_critic'], models['actor_opt'], models['critic_opt'] = create_model(ACTION_DIM, DEVICE)
        models['log_alpha'] = torch.zeros(1, requires_grad=True, device=DEVICE)
        models['alpha_opt'] = torch.optim.Adam([models['log_alpha']], lr=LR)
        return 0, models

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
    
    return load_checkpoint(latest_ckpt, device)

def load_checkpoint(path, device):
    models = dict()
    models['actor'], models['critic'], models['target_critic'], models['actor_opt'], models['critic_opt'] = create_model(ACTION_DIM, DEVICE)
    models['log_alpha'] = torch.zeros(1, requires_grad=True, device=DEVICE)
    models['alpha_opt'] = torch.optim.Adam([models['log_alpha']], lr=LR)
    checkpoint = torch.load(path, map_location=device)
    models['actor'].load_state_dict(checkpoint['actor_state_dict'])
    models['actor_opt'].load_state_dict(checkpoint['actor_opt_state_dict'])
    models['critic'].load_state_dict(checkpoint['critic_state_dict'])
    models['critic_opt'].load_state_dict(checkpoint['critic_opt_state_dict'])
    models['target_critic'].load_state_dict(models['critic'].state_dict())
    models['alpha_opt'].load_state_dict(checkpoint['alpha_opt_state_dict'])
    models['log_alpha'].data.copy_(checkpoint['log_alpha_opt'])
    models['global_step'] = checkpoint.get('total_updates', 0)
    return checkpoint['episode'] + 1, models

def build_pose(task):
    s = task['start_pose']
    t = task['target_pose']
    
    start = carla.Transform(
        carla.Location(x=s['x'], y=s['y'], z=s['z']),
        carla.Rotation(yaw=s['rotate'])
    )
    target = carla.Location(x=t['x'], y=t['y'], z=t['z'])
    
    return start, target

def preprocess_obs(visual, goal, device):
    """
    统一处理函数：支持单帧或 Batch 输入
    输入 visual: (Batch, 4, H, W, 3) 或 (4, H, W, 3)
    """
    v = torch.as_tensor(visual, dtype=torch.uint8, device=device).float()
    g = torch.as_tensor(goal, dtype=torch.float32, device=device)

    # 2. 处理维度 (如果是单条数据，增加 Batch 维度)
    if v.dim() == 4: # (4, H, W, 3)
        v = v.unsqueeze(0) # (1, 4, H, W, 3)
    if g.dim() == 1:
        g = g.unsqueeze(0)

    # 3. 变换通道: (B, 4, H, W, 3) -> (B, 4, 3, H, W) -> (B, 12, H, W)
    # 只有当它是 5 维原始数据时才变换
    if v.dim() == 5:
        v = v.permute(0, 1, 4, 2, 3).reshape(v.shape[0], 12, v.shape[2], v.shape[3])

    # 4. 归一化 (关键：确保只在这里做一次)
    if v.max() > 1.0:
        v = v / 255.0
        
    return v, g

def get_task_info(file_path):
    with open(file_path, 'r') as f:
        scenarios = json.load(f)

    available_towns = list(scenarios.keys())
    town_task_lists = {}
    for town in available_towns:
        tasks_in_this_town = []
        for junction_name in sorted(scenarios[town].keys()):
            junction_data = scenarios[town][junction_name]
            if isinstance(junction_data, dict) and 'tasks' in junction_data:
                for t in junction_data['tasks']:
                    # if t.get('valid') == True:
                    #     t['junction_name'] = junction_name 
                    #     tasks_in_this_town.append(t)
                    t['junction_name'] = junction_name 
                    tasks_in_this_town.append(t)
        town_task_lists[town] = tasks_in_this_town

    return town_task_lists, available_towns

from itertools import cycle

def get_task_stream(town_task_lists, available_towns, locked_town=None):
    """
    locked_town: 如果指定，则只在这个 town 里循环
    """
    if locked_town:
        # 检查指定的地图是否在可用列表中
        actual_towns = [t for t in available_towns if t.lower() == locked_town.lower()]
    else:
        actual_towns = available_towns

    town_cycle = cycle(actual_towns)
    for town in town_cycle:
        tasks = town_task_lists[town]
        random.shuffle(tasks)
        for task in tasks:
            yield town, task

def send_mail(subject,body):
    sender_email = SENDER_EMAIL
    receiver_email = RECEIVER_EMAIL
    password = SENDER_EMAIL_PASSWORD

    # 创建邮件内容
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # 邮件正文
    message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()  # 启用加密
        server.login(sender_email, password)  # 登录
        server.send_message(message)  # 发送
        print("邮件发送成功！")
    except Exception as e:
        print(f"邮件发送失败: {e}")
    finally:
        server.quit()