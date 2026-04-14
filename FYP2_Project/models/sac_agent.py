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
        self.agent_buffer = deque(maxlen=agent_capacity) # 
        self.expert_buffer = []
        self.device = device

    def add_agent_experience(self, state, action, reward, next_state, done):
        self.agent_buffer.append((state, action, reward, next_state, done))

    def clear_expert_data(self):
        self.expert_buffer = [] # 或者你在类中定义的专家列表
        print("--- Expert Buffer Cleared ---")

    # 在 MixedReplayBuffer 类中增加
    def load_expert_data(self, expert_data_root):
        # 查找目录下所有的 pkl 文件
        pkl_files = glob.glob(os.path.join(expert_data_root, "**/*.pkl"), recursive=True)
        print(f"--- Loading expert data, total {len(pkl_files)} task files ---")

        pbar = tqdm(pkl_files, desc="Loading Expert Data", unit="file")
        
        for f_path in pbar:
            try:
                with open(f_path, 'rb') as f:
                    episode_data = pickle.load(f) # 这是一个列表，包含该 episode 的所有 step
                    for transition in episode_data:
                        obs_v = np.array(transition['obs']['visual'], dtype=np.uint8)
                        obs_g = np.array(transition['obs']['goal'], dtype=np.float32)
                        next_obs_v = np.array(transition['next_obs']['visual'], dtype=np.uint8)
                        next_obs_g = np.array(transition['next_obs']['goal'], dtype=np.float32)
                        
                        # transition 格式: {'obs':..., 'action':..., 'reward':..., 'next_obs':..., 'done':...}
                        self.expert_buffer.append((
                            obs_v, obs_g,
                            transition['action'], 
                            transition['reward'], 
                            next_obs_v, next_obs_g,
                            transition['done']
                        ))
            except (pickle.UnpicklingError, EOFError, MemoryError) as e:
                print(f"\n[WARNING] 跳过损坏的专家文件: {f_path} | 错误: {e}")
                
            pbar.set_postfix({"buffer_size": len(self.expert_buffer)})
        print(f"--- Loaded, Size: {len(self.expert_buffer)} ---")

    def sample(self, batch_size=32):
        # 提升 1：避免 list 转换，直接通过索引随机抽取
        indices_a = np.random.randint(0, len(self.agent_buffer), batch_size)
        indices_e = np.random.randint(0, len(self.expert_buffer), batch_size)

        batch_obs_v, batch_obs_g, batch_act, batch_rew, batch_nobs_v, batch_nobs_g, batch_done = [], [], [], [], [], [], []

        # 采样 Agent 经验
        for idx in indices_a:
            data = self.agent_buffer[idx]
            batch_obs_v.append(torch.ByteTensor(data[0]['visual'])) # 确保是 Tensor
            batch_obs_g.append(torch.FloatTensor(data[0]['goal']))
            batch_act.append(data[1])
            batch_rew.append(data[2])
            batch_nobs_v.append(torch.ByteTensor(data[3]['visual']))
            batch_nobs_g.append(torch.FloatTensor(data[3]['goal']))
            batch_done.append(data[4])

        # 采样专家经验 (专家已经是 Tensor 了，速度极快)
        for idx in indices_e:
            data = self.expert_buffer[idx]
            batch_obs_v.append(data[0]); batch_obs_g.append(data[1])
            batch_act.append(data[2]); batch_rew.append(data[3])
            batch_nobs_v.append(data[4]); batch_nobs_g.append(data[5])
            batch_done.append(data[6])

        # 提升 2：使用 torch.stack 进行并行堆叠，并一次性移到 GPU
        def finalize(data_list, is_image=False):
            t = torch.as_tensor(np.array(data_list), device=self.device)
            return t.float() / 255.0 if is_image else t.float()

        return (
            {
                'visual': finalize(batch_obs_v, True), 
                'goal': finalize(batch_obs_g)
            },
            finalize(batch_act),
            finalize(batch_rew).unsqueeze(1),
            {
                'visual': finalize(batch_nobs_v, True),
                'goal': finalize(batch_nobs_g)
            },
            finalize(batch_done).unsqueeze(1)
        )