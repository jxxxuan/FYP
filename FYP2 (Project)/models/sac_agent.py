import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributions import Normal

class Actor(nn.Module):
    def __init__(self, vit_encoder, action_dim):
        super(Actor, self).__init__()
        self.vit = vit_encoder 
        
        # 论文提到的三层全连接层 (258 = 256特征 + 2维目标向量)
        self.fc1 = nn.Linear(258, 128)
        self.fc2 = nn.Linear(128, 32)
        
        self.mu_head = nn.Linear(32, action_dim)
        self.sigma_head = nn.Linear(32, action_dim)

    def forward(self, visual_obs, goal_vector):
        # 1. 维度转换 [B, 4, img_dim, img_dim, 3] -> [B, 4, 3, img_dim, img_dim]
        # 因为 PyTorch 的卷积层要求 Channel 在前
        x = visual_obs.permute(0, 1, 4, 2, 3)
        
        # 2. 合并帧和通道 [B, 12, img_dim, img_dim] (4帧 * 3通道)
        B, f, C, H, W = x.shape
        x = x.reshape(B, f * C, H, W)
        
        # 3. 归一化 (这是 ViT 训练成功的关键)
        # 图像原始是 0-255，ViT 更喜欢 0.0-1.0
        x = x.float() / 255.0
        
        # 4. 进入 ViT 提取特征
        h_t = self.vit(x)  # 得到 256 维特征
        
        # 5. 拼接 2 维目标向量 -> 258 维
        d_t = torch.cat([h_t, goal_vector], dim=-1) 
        
        # 6. 后续全连接层
        x = F.relu(self.fc1(d_t))
        x = F.relu(self.fc2(x))
        
        mu = self.mu_head(x)
        log_sigma = torch.clamp(self.sigma_head(x), -20, 2)
        return mu, log_sigma.exp()

    def sample_action(self, visual_obs, goal_vector):
        mu, sigma = self.forward(visual_obs, goal_vector)
        # 确保分布的参数都在同一个设备上
        dist = Normal(mu, sigma)
        z = dist.rsample() 
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
        # 1. 维度转换 [B, 4, img_dim, img_dim, 3] -> [B, 12, img_dim, img_dim]
        x = visual_obs.permute(0, 1, 4, 2, 3)
        B, f, C, H, W = x.shape
        x = x.reshape(B, f * C, H, W).float() / 255.0
        
        # 2. 提取特征
        h_t = self.vit(x)
        
        # 3. 拼接 Q 值输入
        d_t_action = torch.cat([h_t, goal_vector, action], dim=-1)
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