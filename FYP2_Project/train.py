import torch
import torch.optim as optim
import numpy as np
from envs.carla_env import CarlaEnv
from models.sac_agent import Actor, DoubleCritic, MixedReplayBuffer
from models.vit import ViTEncoder
import torch.nn.functional as F
from torch.utils.tensorboard import SummaryWriter
from dotenv import load_dotenv
import os
import time
from hyperparameter import *
from constants import IMG_DIM_X, IMG_DIM_Y, LOG_DIR, CHECK_POINT_INTERVAL, ED_DIR, CP_DIR, DRIVE_PATH, EPISODES_PER_SWITCH
import json
import random
import carla
import glob
import re

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"--- Device: {device} ({torch.cuda.get_device_name(0)}) ---")

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

def save_checkpoint(actor, critic, episode):
    if not os.path.exists(CP_DIR):
        os.makedirs(CP_DIR)
    
    # 构造保存文件名
    timestamp = time.strftime("%m%d-%H%M")
    filename = os.path.join(CP_DIR, f"sac_carla_ep{episode}_{timestamp}.pth")
    
    torch.save({
        'episode': episode,
        'actor_state_dict': actor.state_dict(),
        'critic_state_dict': critic.state_dict(),
    }, filename)
    print(f"\n[SUCCESS] Saved to: {filename}")

def load_latest_checkpoint(actor, critic, target_critic):
    if not os.path.exists(CP_DIR):
        print(f"--- dir {CP_DIR} not exist ---")
        return 0
    
    # 1. 获取文件夹下所有 .pth 文件
    ckpt_files = glob.glob(os.path.join(CP_DIR, "*.pth"))
    
    if not ckpt_files:
        print("--- No Checkpoint file ---")
        return 0

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
        return 0

    # 4. 执行加载逻辑
    print(f"--- Latest Checkpoint: {latest_ckpt}---")
    checkpoint = torch.load(latest_ckpt, map_location=device)
    
    actor.load_state_dict(checkpoint['actor_state_dict'])
    critic.load_state_dict(checkpoint['critic_state_dict'])
    target_critic.load_state_dict(critic.state_dict())
    
    return checkpoint['episode'] + 1

def train(env, scenarios, actor, critic, target_critic, expert_data_dir, start_episode):

    # 实例化 Actor 和 Double Critic
    writer = SummaryWriter(log_dir=LOG_DIR)
    
    target_critic.load_state_dict(critic.state_dict())
    for param in target_critic.parameters():
        param.requires_grad = False
    
    # 优化器
    actor_opt = optim.Adam(actor.parameters(), lr=LR)
    critic_opt = optim.Adam(critic.parameters(), lr=LR)
    
    # 2. 初始化混合缓冲区
    buffer = MixedReplayBuffer(device, agent_capacity=20000)

    loaded_expert_town = None

    scaler = torch.amp.GradScaler('cuda')

    total_updates = start_episode * 50
    
    available_towns = list(scenarios.keys())

    town_task_lists = {}
    for town in available_towns:
        tasks_in_this_town = []
        for junction_name in sorted(scenarios[town].keys()):
            # 兼容你的 JSON 嵌套结构
            junction_data = scenarios[town][junction_name]
            if isinstance(junction_data, dict) and 'tasks' in junction_data:
                valid_tasks = [t for t in junction_data['tasks'] if t.get('valid') == True]
                tasks_in_this_town.extend(valid_tasks)
        town_task_lists[town] = tasks_in_this_town

    town_pointers = {town: 0 for town in available_towns}
    current_town_idx = 0

    # 2. 初始化各 Town 的当前任务指针
    try:
        # 3. 主训练循环
        for current_episode in range(start_episode, 2000):  # 论文实验进行了2000个回次
            current_town = available_towns[current_town_idx]
            all_tasks = town_task_lists[current_town]

            if town_pointers[current_town] >= len(all_tasks):
                # 重置该地图指针
                town_pointers[current_town] = 0
                # 切换到下一个地图
                current_town_idx = (current_town_idx + 1) % len(available_towns)
                current_town = available_towns[current_town_idx]
                all_tasks = town_task_lists[current_town]
                print(f"\n>>>>>>> {available_towns[current_town_idx-1]} 完成一轮，切换至 {current_town} <<<<<<<")

            task = all_tasks[town_pointers[current_town]]
            town_pointers[current_town] += 1

            should_record = (current_episode % CHECK_POINT_INTERVAL == 0)
            video_file = None
            if should_record:
                video_name = f"debug_{current_town}_ep{current_episode}.mp4"
                video_file = os.path.join(CP_DIR, video_name) # 确保 RECORD_DIR 已定义
                print(f"--- [RECORDING] Start: {video_name} ---")

            if current_town != loaded_expert_town:
                print(f"\n--- Switching Expert Data to: {current_town} ---")
                # 构造当前地图的专家文件夹路径，例如: expert_data/Town03
                specific_expert_dir = os.path.join(expert_data_dir, current_town)
                
                # 清空旧数据并加载新场景数据
                buffer.clear_expert_data() 
                buffer.load_expert_data(specific_expert_dir)
                
                loaded_expert_town = current_town
                # 切换地图后手动清理显存碎片
                torch.cuda.empty_cache()

            print(f"[{current_episode}] scenario: {current_town} | junction index: {task['task_id']}/{len(all_tasks)}")

            s = task['start_pose']
            t = task['target_pose']
            start_transform = carla.Transform(
                    carla.Location(x=s['x'], y=s['y'], z=s['z']), # 抬高防卡地
                    carla.Rotation(yaw=s['rotate'])
                )
            target_loc = carla.Location(x=t['x'], y=t['y'], z=t['z'])
            obs, _ = env.reset(current_town, video_path = video_file, start_transform=start_transform, target_location=target_loc)
            episode_reward = 0

            for step in range(500):  # 每回次最大步数
                # 选择动作
                action_tensor,_ = actor.sample_action_with_logprob(
                    torch.FloatTensor(obs['visual']).unsqueeze(0).cuda(),
                    torch.FloatTensor(obs['goal']).unsqueeze(0).cuda()
                )
                action_numpy = action_tensor.detach().cpu().numpy()[0]
                # 环境交互
                next_obs, reward, terminated, truncated, info = env.step(action_numpy)
                
                # 保存到智能体缓冲区
                buffer.add_agent_experience(obs, action_numpy, reward, next_obs, terminated)
                
                # 开始更新网络 (如果缓冲区数据足够)
                if step % 10 == 0 and len(buffer.agent_buffer) > 500:
                    for _ in range(2):
                        # 混合采样：32个智能体样本 + 32个专家样本
                        b_s, a, r, b_ns, d = buffer.sample(BATCH_SIZE_A, BATCH_SIZE_E)
                        s_v, s_g = b_s['visual'], b_s['goal']
                        ns_v, ns_g = b_ns['visual'], b_ns['goal']
                        
                        with torch.no_grad():
                            with torch.autocast(device_type="cuda"):
                                # 获取下一状态的动作和 log_prob
                                next_action, next_log_prob = actor.sample_action_with_logprob(ns_v, ns_g)
                                # 使用 Target Critic 计算目标
                                target_q1, target_q2 = target_critic(ns_v, ns_g, next_action)
                                target_q = torch.min(target_q1, target_q2) - ALPHA * next_log_prob
                                # 计算 y (Reward + Gamma * Target_Q)
                                y = r + GAMMA * (1 - d) * target_q

                        # Critic 更新
                        with torch.autocast(device_type="cuda"):
                            curr_q1, curr_q2 = critic(s_v, s_g, a)
                            critic_loss = F.mse_loss(curr_q1, y) + F.mse_loss(curr_q2, y)
                        critic_opt.zero_grad()
                        scaler.scale(critic_loss).backward()
                        scaler.step(critic_opt)
                        scaler.update()

                        # Actor 更新
                        for p in critic.parameters(): p.requires_grad = False

                        with torch.autocast(device_type="cuda"):
                            new_action, log_prob = actor.sample_action_with_logprob(s_v, s_g)
                            q1, q2 = critic(s_v, s_g, new_action)
                            actor_loss = (ALPHA * log_prob - torch.min(q1, q2)).mean()
                        actor_opt.zero_grad()
                        scaler.scale(actor_loss).backward()
                        scaler.step(actor_opt)

                        for p in critic.parameters(): p.requires_grad = True

                        scaler.update()
                        
                        # --- 软更新目标网络 ---
                        for param, target_param in zip(critic.parameters(), target_critic.parameters()):
                            target_param.data.copy_(TAU * param.data + (1 - TAU) * target_param.data)

                        total_updates += 1
                        writer.add_scalar('Loss/Critic', critic_loss.item(), total_updates)
                        writer.add_scalar('Loss/Actor', actor_loss.item(), total_updates)
                
                obs = next_obs
                episode_reward += reward
                if terminated or truncated:
                    break

            writer.add_scalar('Reward/Episode', episode_reward, current_episode)
            print("reward: ", episode_reward)
            if should_record:
                save_checkpoint(actor, critic, current_episode)
    except KeyboardInterrupt:
        print("\n[DETECTED] Ctrl+C")
    except Exception as e:
        print(f"\n[ERROR] : {e}")
        raise e # 重新抛出异常以便调试
    finally:
        writer.close()
        print("Saved")
        env.close()

if __name__ == '__main__':
    with open(os.path.join(DRIVE_PATH, 'train_tasks.json'), 'r') as f:
        scenarios = json.load(f)

    # 1. Actor 的视觉编码器
    vit_encoder_a = create_vit()

    # 2. Critic 的视觉编码器 (用于 Double Q)
    # 论文中 Critic 网络共享相同的 ViT 架构 
    shared_vit_c = create_vit()

    # 3. Target Critic 的视觉编码器 (用于稳定训练) [cite: 227]
    shared_vit_tc = create_vit()

    # 初始化环境与模型
    env = CarlaEnv()
    action_dim = env.action_space.shape[0]

    actor = Actor(vit_encoder_a, action_dim).to(device)
    critic = DoubleCritic(shared_vit_c, shared_vit_c, action_dim).to(device)
    target_critic = DoubleCritic(shared_vit_tc, shared_vit_tc, action_dim).to(device)

    start_episode = load_latest_checkpoint(actor, critic, target_critic)
    print(start_episode)

    train(env, scenarios, actor, critic, target_critic, ED_DIR, start_episode)