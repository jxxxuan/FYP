import json
import random
import pandas as pd
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
from models.sac_agent import Actor, DoubleCritic, SharedViTSAC

def create_vit():
    return ViTEncoder(
        img_size_h=IMG_DIM_Y, 
        img_size_w=IMG_DIM_X*NUM_CAM, 
        patch_size=PATCH_SIZE, 
        in_chans=IN_CHANNEL,
        embed_dim=EMBED_DIM, 
        depth=DEPTH, 
        num_heads=HEADS
    )

def create_model(action_dim, device):
    vit_encoder_a = create_vit()

    # 2. Critic's visual encoder (used for Double Q)
    shared_vit_c1 = create_vit()
    shared_vit_c2 = create_vit()

    # 3. Target Critic's visual encoder (used for stable training) [cite: 227]
    shared_vit_tc1 = create_vit()
    shared_vit_tc2 = create_vit()

    actor = Actor(vit_encoder_a, action_dim).to(device)
    
    critic = DoubleCritic(shared_vit_c1, shared_vit_c2, action_dim).to(device)
    target_critic = DoubleCritic(shared_vit_tc1, shared_vit_tc2, action_dim).to(device)

    actor_opt = optim.Adam(actor.parameters(), lr=LR)
    critic_opt = optim.Adam(critic.parameters(), lr=LR)

    return actor, critic, target_critic, actor_opt, critic_opt

def save_checkpoint(models, episode):
    if not os.path.exists(CP_DIR):
        os.makedirs(CP_DIR)
    
    timestamp = time.strftime("%m%d-%H%M")
    filename = os.path.join(CP_DIR, f"ep{episode}_{timestamp}.pth")
    
    raw_actor = models['actor']._orig_mod if hasattr(models['actor'], "_orig_mod") else models['actor']
    raw_critic = models['critic']._orig_mod if hasattr(models['critic'], "_orig_mod") else models['critic']

    torch.save({
        'episode': episode,
        'global_step': models['global_step'],
        'actor_state_dict': raw_actor.state_dict(),
        'critic_state_dict': raw_critic.state_dict(),
        'actor_opt_state_dict': models['actor_opt'].state_dict(),
        'critic_opt_state_dict': models['critic_opt'].state_dict(),
        'log_alpha_opt': models['log_alpha'],           # Must save this tensor
        'alpha_opt_state_dict': models['alpha_opt'].state_dict(), # Must save its optimizer
    }, filename)
    print(f"\n[SUCCESS] Saved to: {filename}")

def init_models():
    models = dict()
    models['actor'], models['critic'], models['target_critic'], models['actor_opt'], models['critic_opt'] = create_model(ACTION_DIM, DEVICE)
    models['log_alpha'] = torch.zeros(INIT_ALPHA, requires_grad=True, device=DEVICE)
    models['alpha_opt'] = torch.optim.Adam([models['log_alpha']], lr=LR)
    models['global_step'] = 0
    models['episode'] = 0
    return models

def load_latest_checkpoint(device):
    # 1. Get all .pth files in the directory
    ckpt_files = glob.glob(os.path.join(CP_DIR, "*.pth"))
    
    if not ckpt_files:
        print("--- No Checkpoint file ---")
        models = init_models()
        # models = init_share_models()
        return models

    # 2. Define helper function to extract episode number from filename
    # Assume filename format is sac_carla_ep150_...
    def extract_episode(filename):
        match = re.search(r'ep(\d+)', filename)
        return int(match.group(1)) if match else -1

    # 3. Find file with the maximum episode number
    latest_ckpt = max(ckpt_files, key=extract_episode)
    max_ep = extract_episode(latest_ckpt)

    if max_ep == -1:
        print("--- Filename format mismatch (no 'ep' number found), please check filename ---")
        models = init_models()
        return models

    # 4. Execute loading logic
    print(f"--- Latest Checkpoint: {latest_ckpt}---")
    
    return load_checkpoint(latest_ckpt, device)
    # return load_share_checkpoint(latest_ckpt, device)

def load_checkpoint(path, device):
    models = init_models()
    checkpoint = torch.load(path, map_location=device)
    models['actor'].load_state_dict(checkpoint['actor_state_dict'])
    models['actor_opt'].load_state_dict(checkpoint['actor_opt_state_dict'])
    models['critic'].load_state_dict(checkpoint['critic_state_dict'])
    models['critic_opt'].load_state_dict(checkpoint['critic_opt_state_dict'])
    models['target_critic'].load_state_dict(models['critic'].state_dict())
    models['alpha_opt'].load_state_dict(checkpoint['alpha_opt_state_dict'])
    models['log_alpha'].data.copy_(checkpoint['log_alpha_opt'])
    models['global_step'] = checkpoint.get('global_step', 0)
    models['episode'] = checkpoint.get('episode', 0) + 1
    return models

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
    Unified preprocessing function: supports single frame or batch input
    Input visual: (Batch, 4, H, W, 3) or (4, H, W, 3)
    """
    v = torch.as_tensor(visual, dtype=torch.uint8, device=device).float()
    g = torch.as_tensor(goal, dtype=torch.float32, device=device)

    # 2. Handle dimension (if single sample, add Batch dimension)
    if v.dim() == 4: # (4, H, W, 3)
        v = v.unsqueeze(0) # (1, 4, H, W, 3)
    if g.dim() == 1:
        g = g.unsqueeze(0)

    # 3. Transpose channels: (B, 4, H, W, 3) -> (B, 4, 3, H, W) -> (B, 12, H, W)
    # Only transpose if it is 5D raw data
    if v.dim() == 5:
        v = v.permute(0, 1, 4, 2, 3).reshape(v.shape[0], 12, v.shape[2], v.shape[3])

    # 4. Normalization (Key: ensure it is done only once here)
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
    locked_town: if specified, loop only within this town
    """
    if locked_town:
        # Check if the specified map is in the available list
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

    # Create email content
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # Email body
    message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()  # Enable encryption
        server.login(sender_email, password)  # Login
        server.send_message(message)  # Send
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
    finally:
        server.quit()

def load_latest_record(train=True):
    if train:
        log_path = TRAIN_LOG_DIR
    else:
        log_path = TEST_LOG_DIR

    if not os.path.exists(log_path):
        print("--- No train log found ---")
        return []

    try:
        records = pd.read_csv(log_path).to_dict('records')
        print(f"--- Loaded {len(records)} training records ---")
        return records

    except Exception as e:
        print(f"--- Failed to load train log: {e} ---")
        return []
    
def save_record(records, train=True):
    if train:
        pd.DataFrame(records).to_csv(TRAIN_LOG_DIR, index=False)
    else:
        pd.DataFrame(records).to_csv(TEST_LOG_DIR, index=False)

def save_record(data, type='train'):
    """
    General save function
    type: 'train' (training logs), 'test_summary' (100 trials summary), 'test_raw' (100 trials raw data)
    """
    if type == 'train':
        pd.DataFrame(data).to_csv(TRAIN_LOG_DIR, index=False)
    
    elif type == 'test_summary':
        # Save the 100 trials raw data for this specific episode, with ep_num in filename
        pd.DataFrame(data).to_csv(DETAIL_LOG_DIR, index=False)
        
    elif type == 'test_raw':
        df = pd.DataFrame([data] if isinstance(data, dict) else data)
        # Use append mode to save to the summary table
        header = not os.path.exists(TEST_LOG_DIR)
        df.to_csv(TEST_LOG_DIR, mode='a', index=False, header=header)