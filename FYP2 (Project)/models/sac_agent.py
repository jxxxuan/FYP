import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributions import Normal

class Actor(nn.Module):
    def __init__(self, vit_encoder, action_dim):
        super(Actor, self).__init__()
        self.vit = vit_encoder  # 之前实现的 ViTEncoder
        
        # 论文提到的三层全连接层 
        self.fc1 = nn.Linear(258, 128)
        self.fc2 = nn.Linear(128, 32)
        
        # 输出均值和标准差 
        self.mu_head = nn.Linear(32, action_dim)
        self.sigma_head = nn.Linear(32, action_dim)

    def forward(self, visual_obs, goal_vector):
        h_t = self.vit(visual_obs)  # 256维
        # 拼接成 258 维 [cite: 196]
        d_t = torch.cat([h_t, goal_vector], dim=-1) 
        
        x = F.relu(self.fc1(d_t))
        x = F.relu(self.fc2(x))
        
        mu = self.mu_head(x)
        # 使用 log_std 确保标准差为正
        log_sigma = torch.clamp(self.sigma_head(x), -20, 2)
        return mu, log_sigma.exp()

    def sample_action(self, visual_obs, goal_vector):
        mu, sigma = self.forward(visual_obs, goal_vector)
        dist = Normal(mu, sigma)
        z = dist.rsample()
        # 使用 tanh 限制动作在 [-1, 1] 范围内
        action = torch.tanh(z)
        return action
    
class Critic(nn.Module):
    def __init__(self, vit_encoder, action_dim):
        super(Critic, self).__init__()
        self.vit = vit_encoder  # 共享或独立的 ViT 特征提取器 
        
        # 输入维度 = 256 (ViT输出) + 2 (目标向量) + action_dim (动作)
        input_dim = 256 + 2 + action_dim
        
        # 论文提到的 MLP 架构
        self.fc1 = nn.Linear(input_dim, 128)
        self.fc2 = nn.Linear(128, 32)
        self.q_out = nn.Linear(32, 1)

    def forward(self, visual_obs, goal_vector, action):
        # 1. 提取视觉特征 H_t [cite: 171]
        h_t = self.vit(visual_obs)
        
        # 2. 拼接特征、目标向量和动作 [cite: 161]
        d_t_action = torch.cat([h_t, goal_vector, action], dim=-1)
        
        # 3. 通过全连接层得到 Q 值
        x = F.relu(self.fc1(d_t_action))
        x = F.relu(self.fc2(x))
        return self.q_out(x)

class DoubleCritic(nn.Module):
    def __init__(self, vit_c1, vit_c2, action_dim):
        super(DoubleCritic, self).__init__()
        # 实例化两个独立的 Q 网络，分别传入不同的 ViT 实例
        self.Q1 = Critic(vit_c1, action_dim)
        self.Q2 = Critic(vit_c2, action_dim)

    def forward(self, visual_obs, goal_vector, action):
        q1 = self.Q1(visual_obs, goal_vector, action)
        q2 = self.Q2(visual_obs, goal_vector, action)
        return q1, q2
    
import random
from collections import deque

class MixedReplayBuffer:
    def __init__(self, agent_capacity=200000):
        self.agent_buffer = deque(maxlen=agent_capacity) # 
        self.expert_buffer = [] # 存储那 13,542 条专家数据 [cite: 244]

    def add_agent_experience(self, state, action, reward, next_state, done):
        self.agent_buffer.append((state, action, reward, next_state, done))

    def load_expert_data(self, expert_data_path):
        # 加载离线收集的专家数据 [cite: 245]
        pass

    def sample(self, batch_size_a=32, batch_size_e=32):
        # 严格复刻：从两个池子分别采样并拼接 
        batch_a = random.sample(self.agent_buffer, batch_size_a)
        batch_e = random.sample(self.expert_buffer, batch_size_e)
        return batch_a + batch_e