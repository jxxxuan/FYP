import torch
import torch.optim as optim
import numpy as np
from envs.carla_env import CarlaEnv
from models.sac_agent import Actor, DoubleCritic, MixedReplayBuffer
from models.vit import ViTEncoder
import torch.nn.functional as F
from dotenv import load_dotenv
import os
import time
from hyperparameter import *

load_dotenv()

img_dim = int(os.getenv("IMG_DIM"))

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"--- 确认设备: {device} ({torch.cuda.get_device_name(0)}) ---")

def create_vit():
    return ViTEncoder(
        img_size=img_dim, 
        patch_size=14, 
        in_chans=12,
        embed_dim=256, 
        depth=2, 
        num_heads=1
    )

def train():
    # 初始化环境与模型
    env = CarlaEnv()
    action_dim = env.action_space.shape[0]
    
    # 实例化 Actor 和 Double Critic
    actor = Actor(vit_encoder_a, action_dim).to(device)
    critic = DoubleCritic(vit_encoder_c1, vit_encoder_c2, action_dim).to(device)
    target_critic = DoubleCritic(vit_encoder_tc1, vit_encoder_tc2, action_dim).to(device)
    target_critic.load_state_dict(critic.state_dict())
    
    # 优化器
    actor_opt = optim.Adam(actor.parameters(), lr=LR)
    critic_opt = optim.Adam(critic.parameters(), lr=LR)
    
    # 2. 初始化混合缓冲区
    buffer = MixedReplayBuffer(agent_capacity=200000)
    buffer.load_expert_data("data/expert_demos/expert_data.pkl") # 13,542条专家数据

    # 3. 主训练循环
    for episode in range(2000):  # 论文实验进行了2000个回次
        obs, _ = env.reset()
        episode_reward = 0
        
        for step in range(500):  # 每回次最大步数
            print("training: ",step)
            time.sleep(0.1)
            # print('episode: ',episode)
            # 选择动作
            action = actor.sample_action(
                torch.FloatTensor(obs['visual']).unsqueeze(0).cuda(),
                torch.FloatTensor(obs['goal']).unsqueeze(0).cuda()
            )
            
            # 环境交互
            next_obs, reward, terminated, truncated, info = env.step(action)
            
            # 保存到智能体缓冲区
            buffer.add_agent_experience(obs, action, reward, next_obs, terminated)
            
            # 开始更新网络 (如果缓冲区数据足够)
            if len(buffer.agent_buffer) > 1000:
                # 混合采样：32个智能体样本 + 32个专家样本
                b_s, b_a, b_r, b_ns, b_d = buffer.sample(BATCH_SIZE_A, BATCH_SIZE_E)

                s_v = torch.FloatTensor(b_s['visual']).to(device)
                s_g = torch.FloatTensor(b_s['goal']).to(device)
                a = torch.FloatTensor(b_a).to(device)
                r = torch.FloatTensor(b_r).unsqueeze(1).to(device) # 增加维度以匹配 Q 值
                d = torch.FloatTensor(b_d).unsqueeze(1).to(device)

                ns_v = torch.FloatTensor(b_ns['visual']).to(device)
                ns_g = torch.FloatTensor(b_ns['goal']).to(device)
                
                # --- 更新 Critic (Equation 9) ---
                with torch.no_grad():
                    print('updating')
                    # 计算目标 Q 值，使用双重网络最小值
                    next_action, next_log_prob = actor.sample_action_with_logprob(ns_v, ns_g) 
                    target_q1, target_q2 = target_critic(ns_v, ns_g, next_action)
                    target_q = torch.min(target_q1, target_q2) - ALPHA * next_log_prob
                    y = r + GAMMA * (1 - d) * target_q
                
                curr_q1, curr_q2 = critic(s_v, s_g, a)
                critic_loss = F.mse_loss(curr_q1, y) + F.mse_loss(curr_q2, y)
                
                critic_opt.zero_grad()
                critic_loss.backward()
                critic_opt.step()
                
                # --- 更新 Actor (Equation 11) ---
                new_action, log_prob = actor.sample_action_with_logprob(s_v, s_g)
                q1, q2 = critic(s_v, s_g, new_action)
                actor_loss = (ALPHA * log_prob - torch.min(q1, q2)).mean()
                
                actor_opt.zero_grad()
                actor_loss.backward()
                actor_opt.step()
                
                # --- 软更新目标网络 ---
                for param, target_param in zip(critic.parameters(), target_critic.parameters()):
                    target_param.data.copy_(TAU * param.data + (1 - TAU) * target_param.data)
            
            obs = next_obs
            episode_reward += reward
            if terminated or truncated:
                break
    env.close()

if __name__ == '__main__':
    # 1. Actor 的视觉编码器
    vit_encoder_a = create_vit()

    # 2. Critic 的视觉编码器 (用于 Double Q)
    # 论文中 Critic 网络共享相同的 ViT 架构 
    vit_encoder_c1 = create_vit()
    vit_encoder_c2 = create_vit()

    # 3. Target Critic 的视觉编码器 (用于稳定训练) [cite: 227]
    vit_encoder_tc1 = create_vit()
    vit_encoder_tc2 = create_vit()

    train()