import random
import cv2
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
from hyperparameter import IMG_DIM_X, IMG_DIM_Y

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
        x = visual_obs.float() / 255.0
        
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
        x = visual_obs.float() / 255.0
        h_t = self.vit(x)
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
    def __init__(self, device, agent_capacity=200000):
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
        self.expert_v = torch.empty((total_steps, 12, IMG_DIM_X*2, IMG_DIM_Y), dtype=torch.uint8, device=self.device)
        self.expert_g = torch.empty((total_steps, 2), dtype=torch.float32, device=self.device)
        self.expert_act = torch.empty((total_steps, 2), device=self.device)
        self.expert_rew = torch.empty((total_steps, 1), device=self.device)
        self.expert_nv = torch.empty((total_steps, 12, IMG_DIM_X*2, IMG_DIM_Y), dtype=torch.uint8, device=self.device)
        self.expert_ng = torch.empty((total_steps, 2), dtype=torch.float32, device=self.device)
        self.expert_done = torch.empty((total_steps, 1), device=self.device)

        # 3. 填充阶段：再加上进度条
        ptr = 0
        fill_pbar = tqdm(all_episodes, desc="Filling VRAM Tensors", unit="episode")
        for episode_data in fill_pbar:
            for t in episode_data:
                # --- 处理视觉输入 (Observation) ---
                v_raw = torch.from_numpy(t['obs']['visual']) 

                v_stacked = []
                for i in range(4):
                    # 强行对齐论文规格
                    resized = cv2.resize(v_raw[i], (84, 84)) 
                    v_stacked.append(resized)
                v_processed = torch.from_numpy(np.array(v_stacked)).permute(0, 3, 1, 2).reshape(12, 84, 84)
                # v_processed = v_raw.permute(0, 3, 1, 2).reshape(12, IMG_DIM_X, IMG_DIM_Y)

                self.expert_v[ptr] = v_processed.to(self.device)

                # --- 处理下一帧视觉 (Next Observation) ---
                nv_raw = torch.from_numpy(t['next_obs']['visual'])

                nv_stacked = [cv2.resize(nv_raw[i], (84, 84)) for i in range(4)]
                nv_processed = torch.from_numpy(np.array(nv_stacked)).permute(0, 3, 1, 2).reshape(12, 84, 84)
                # nv_processed = nv_raw.permute(0, 3, 1, 2).reshape(12, IMG_DIM_X, IMG_DIM_Y)

                self.expert_nv[ptr] = nv_processed.to(self.device)

                # --- 其他字段不需要 Reshape，直接存 ---
                self.expert_g[ptr] = torch.from_numpy(t['obs']['goal']).to(self.device)
                self.expert_act[ptr] = torch.from_numpy(t['action']).to(self.device)
                self.expert_rew[ptr] = torch.tensor(t['reward'], device=self.device)
                self.expert_ng[ptr] = torch.from_numpy(t['next_obs']['goal']).to(self.device)
                self.expert_done[ptr] = torch.tensor(t['done'], dtype=torch.float32, device=self.device)
                
                ptr += 1
        
        self.expert_ptr = ptr
        print(f"--- Expert Loaded into VRAM, Size: {self.expert_ptr} ---")

    def sample(self, e_batch_size, a_batch_size):
        # --- 1. Agent 采样 (CPU) ---
        indices_a = random.sample(range(len(self.agent_buffer)), a_batch_size)
        batch_a = [self.agent_buffer[i] for i in indices_a]

        # 转换为 Tensor 并统一增加维度 (unsqueeze) 确保是 2 维
        a_v = torch.as_tensor(np.array([d[0]['visual'] for d in batch_a]), device=self.device)
        a_g = torch.as_tensor(np.array([d[0]['goal'] for d in batch_a]), device=self.device)
        a_act = torch.as_tensor(np.array([d[1] for d in batch_a]), device=self.device)
        
        # 关键修复点：使用 .unsqueeze(1) 把 (128,) 变成 (128, 1)
        a_rew = torch.as_tensor(np.array([d[2] for d in batch_a]), device=self.device).float().unsqueeze(1)
        a_done = torch.as_tensor(np.array([d[4] for d in batch_a]), device=self.device).float().unsqueeze(1)
        
        a_nv = torch.as_tensor(np.array([d[3]['visual'] for d in batch_a]), device=self.device)
        a_ng = torch.as_tensor(np.array([d[3]['goal'] for d in batch_a]), device=self.device)

        # --- 处理视觉维度 ---
        if a_v.dim() == 5: # [B, 4, 96, 256, 3]
            a_v = a_v.permute(0, 1, 4, 2, 3).reshape(a_batch_size, 12, 96, 256)
            a_nv = a_nv.permute(0, 1, 4, 2, 3).reshape(a_batch_size, 12, 96, 256)

        # --- 2. Expert 采样 ---
        idx_e = torch.randint(0, self.expert_ptr, (e_batch_size,), device=self.device)

        # --- 3. 合并函数 ---
        def finalize(agent_tensor, expert_tensor, is_image=False):
            # 此时 agent_tensor 和 expert_tensor 都是 2 维或以上了
            merged = torch.cat([agent_tensor, expert_tensor], dim=0).float()
            return merged / 255.0 if is_image else merged

        # --- 4. 返回结果 ---
        # 注意：因为 a_rew 已经是 (B, 1)，expert_rew 也是 (B, 1)，
        # 这里的 finalize 结果就是 (batch_size_total, 1)，不需要再 unsqueeze(1) 了。
        return (
            {
                'visual': finalize(a_v, self.expert_v[idx_e], True),
                'goal': finalize(a_g, self.expert_g[idx_e])
            },
            finalize(a_act, self.expert_act[idx_e]),
            finalize(a_rew, self.expert_rew[idx_e]), # 移除原来的 .unsqueeze(1)
            {
                'visual': finalize(a_nv, self.expert_nv[idx_e], True),
                'goal': finalize(a_ng, self.expert_ng[idx_e])
            },
            finalize(a_done, self.expert_done[idx_e]) # 移除原来的 .unsqueeze(1)
        )
    
    def sample_expert_only(self, e_batch_size):
        """
        专门为行为克隆 (BC) 预训练提供的采样函数
        只从专家数据中提取样本
        """
        # 1. 随机生成专家数据的索引
        idx_e = torch.randint(0, self.expert_ptr, (e_batch_size,), device=self.device)

        # 2. 提取并处理专家数据
        # 视觉数据需要转为 float 并归一化 (/ 255.0)
        e_v = self.expert_v[idx_e].float() / 255.0
        e_g = self.expert_g[idx_e]
        e_act = self.expert_act[idx_e]
        e_rew = self.expert_rew[idx_e]
        e_nv = self.expert_nv[idx_e].float() / 255.0
        e_ng = self.expert_ng[idx_e]
        e_done = self.expert_done[idx_e]

        # 3. 按照与 sample() 一致的格式返回字典
        return (
            {
                'visual': e_v,
                'goal': e_g
            },
            e_act,
            e_rew,
            {
                'visual': e_nv,
                'goal': e_ng
            },
            e_done
        )