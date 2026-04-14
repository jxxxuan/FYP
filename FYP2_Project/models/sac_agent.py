import random

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributions import Normal
from collections import deque
import numpy as np
import os
import glob
import pickle
from tqdm import tqdm

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
        # 1. 维度转换 [B, 4, img_dim, img_dim*3, 3] -> [B, 4, 3, img_dim, img_dim*3]
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
    
    def sample_action_with_logprob(self, visual_obs, goal_vector):
        mu, sigma = self.forward(visual_obs, goal_vector)
        dist = Normal(mu, sigma)
        z = dist.rsample()
        action = torch.tanh(z)
        log_prob = dist.log_prob(z) - torch.log(1 - action.pow(2) + 1e-6)
        log_prob = log_prob.sum(dim=-1, keepdim=True)
        return action, log_prob
    
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

class MixedReplayBuffer:
    def __init__(self, device, agent_capacity=20000):
        self.agent_buffer = deque(maxlen=agent_capacity)
        self.device = device
        self.expert_ptr = 0

    def add_agent_experience(self, state, action, reward, next_state, done):
        self.agent_buffer.append((state, action, reward, next_state, done))

    def clear_expert_data(self):
        self.expert_ptr = 0 # 只需要重置指针，不需要重新分配显存

    # 在 MixedReplayBuffer 类中增加
    def load_expert_data(self, expert_data_root):
        pkl_files = glob.glob(os.path.join(expert_data_root, "**/*.pkl"), recursive=True)
        
        # 1. 扫描阶段：加上进度条
        total_steps = 0
        all_episodes = []
        scan_pbar = tqdm(pkl_files, desc="Scanning Expert Files", unit="file")
        for f_path in scan_pbar:
            with open(f_path, 'rb') as f:
                episode_data = pickle.load(f)
                total_steps += len(episode_data)
                all_episodes.append(episode_data)
        
        print(f"--- Detected total {total_steps} expert steps ---")

        # 2. 动态创建 Tensor (此步瞬间完成，不需要进度条)
        self.expert_v = torch.empty((total_steps, 12, 96, 256), dtype=torch.uint8, device=self.device)
        self.expert_g = torch.empty((total_steps, 3), dtype=torch.float32, device=self.device)
        self.expert_act = torch.empty((total_steps, 2), device=self.device)
        self.expert_rew = torch.empty((total_steps, 1), device=self.device)
        self.expert_nv = torch.empty((total_steps, 12, 96, 256), dtype=torch.uint8, device=self.device)
        self.expert_ng = torch.empty((total_steps, 3), dtype=torch.float32, device=self.device)
        self.expert_done = torch.empty((total_steps, 1), device=self.device)

        # 3. 填充阶段：再加上进度条
        ptr = 0
        fill_pbar = tqdm(all_episodes, desc="Filling VRAM Tensors", unit="episode")
        for episode_data in fill_pbar:
            for t in episode_data:
                # 已经是 Tensor 的搬运操作，速度会很快
                self.expert_v[ptr] = torch.from_numpy(t['obs']['visual']).to(self.device)
                self.expert_g[ptr] = torch.from_numpy(t['obs']['goal']).to(self.device)
                self.expert_act[ptr] = torch.from_numpy(t['action']).to(self.device)
                self.expert_rew[ptr] = torch.tensor(t['reward'], device=self.device)
                self.expert_nv[ptr] = torch.from_numpy(t['next_obs']['visual']).to(self.device)
                self.expert_ng[ptr] = torch.from_numpy(t['next_obs']['goal']).to(self.device)
                self.expert_done[ptr] = torch.tensor(t['done'], dtype=torch.float32, device=self.device)
                ptr += 1
        
        self.expert_ptr = ptr
        print(f"--- Expert Loaded into VRAM, Size: {self.expert_ptr} ---")

    def sample(self, batch_size_a, batch_size_e):
        # --- 1. Agent 采样 ---
        # 即使只用 128 条，也建议用随机索引减少采样时间
        indices_a = random.sample(range(len(self.agent_buffer)), batch_size_a)
        
        a_v, a_g, a_act, a_rew, a_nv, a_ng, a_done = [], [], [], [], [], [], []
        for i in indices_a:
            d = self.agent_buffer[i]
            # 存储时保持 numpy 格式，采样时转 Tensor
            a_v.append(torch.from_numpy(d[0]['visual']))
            a_g.append(torch.from_numpy(d[0]['goal']))
            a_act.append(torch.from_numpy(d[1]))
            a_rew.append(torch.tensor(d[2]))
            a_nv.append(torch.from_numpy(d[3]['visual']))
            a_ng.append(torch.from_numpy(d[3]['goal']))
            a_done.append(torch.tensor(d[4], dtype=torch.float32))

        # --- 2. Expert 采样 (索引已经在 GPU) ---
        idx_e = torch.randint(0, self.expert_ptr, (batch_size_e,), device=self.device)
        
        # --- 3. 高性能合并 ---
        def finalize(agent_t_list, expert_tensor, is_image=False):
            # 这里的 agent_t_list 已经是 Tensor 列表了
            a_batch = torch.stack(agent_t_list).to(self.device)
            # 关键：在这里合并，一次性处理
            merged = torch.cat([a_batch, expert_tensor], dim=0).float()
            return merged / 255.0 if is_image else merged