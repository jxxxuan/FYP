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
from hyperparameter import IMG_DIM_X, IMG_DIM_Y
from torch.utils.data import DataLoader, TensorDataset
import sys
import cv2
from torch.utils.data import Dataset, DataLoader

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

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
        # 4. 进入 ViT 提取特征
        h_t = self.vit(visual_obs)  # 得到 256 维特征
        
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
        h_t = self.vit(visual_obs)
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

class ObsBuffer:
    def __init__(self, stack):
        self.stack = stack
        self.reset()

    def reset(self):
        # 使用列表存储，动态增长，任务结束后统一转 numpy/tensor 存盘
        self.visual_pool = []
        self.goal_pool = []
        self.action_pool = []
        self.reward_pool = []
        self.debug_frame_pool = []
        self.ptr = -1

    def add(self, visual, goal, action=None, reward=None, debug_frame=None):
        self.visual_pool.append(visual) # uint8 (H, W, 3)
        self.goal_pool.append(goal)     # float (2,)
        if action is not None: self.action_pool.append(action)
        if reward is not None: self.reward_pool.append(reward)
        if debug_frame is not None: self.debug_frame_pool.append(debug_frame)
        self.ptr += 1

    def get_current_obs(self):
        """
        为 RL 训练提供当前时刻的堆叠观察值
        """
        start_idx = max(0, self.ptr - self.stack + 1)
        # 获取最近的 N 帧视觉
        v_frames = self.visual_pool[start_idx : self.ptr + 1]
        # 获取最新的 1 个目标向量 (目标通常不需要堆叠)
        curr_goal = self.goal_pool[self.ptr]

        # 补齐逻辑
        if len(v_frames) < self.stack:
            padding = [v_frames[0]] * (self.stack - len(v_frames))
            v_frames = padding + v_frames
            
        return {
            "visual": np.array(v_frames, dtype=np.uint8), # (4, H, W, 3)
            "goal": np.array(curr_goal, dtype=np.float32)
        }

    def pack_episode(self, success):
        """
        将整个 Episode 压缩成一个紧凑字典，直接传给 pkl
        """
        return {
            "visual_seq": np.array(self.visual_pool, dtype=np.uint8),
            "goal_seq": np.array(self.goal_pool, dtype=np.float32),
            "actions": np.array(self.action_pool, dtype=np.float32),
            "rewards": np.array(self.reward_pool, dtype=np.float32),
            "success": success
        }

    def to_video(self, save_path, fps=20):
        use_debug = len(self.debug_frame_pool) > 0
        print('debug frame:',len(self.debug_frame_pool))
        video_source = self.debug_frame_pool if use_debug else self.visual_pool

        if not video_source:
            print("Buffer is empty, nothing to save.")
            return

        # 1. 获取尺寸 (H, W*2)
        height, width, _ = video_source[0].shape
        size = (width, height)

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(save_path, fourcc, fps, size)

        if width < 500:
            font_scale = 0.25 
            line_height = 8
            bg_width = int(width * 0.8)
        else:
            font_scale = 0.7
            line_height = 35
            bg_width = 450

        thickness = 1
        total_reward = 0
        # 遍历整个 Episode 的线性池
        for i in range(len(video_source)):
            # 转换并确保是 uint8 格式
            img = video_source[i].astype(np.uint8)

            if i < len(self.reward_pool):
                total_reward += self.reward_pool[i]

            # 在画面左上角画个黑框背景，防止文字看不清
            overlay = img.copy()
            cv2.rectangle(overlay, (0, 0), (bg_width, line_height * 2 + 10), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.5, img, 0.5, 0, img)

            curr_goal = self.goal_pool[i]
            text_top = f"TR: {total_reward:.1f} | G:[{curr_goal[0]:.0f},{curr_goal[1]:.0f}]"
            cv2.putText(img, text_top, (5, line_height), 
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)

            # 如果你还存了奖励，也可以写上去
            if i < len(self.reward_pool):
                reward = self.reward_pool[i]
                text_bot = f"R: {reward:.2f}"
                color = (0, 255, 0) if reward >= 0 else (0, 0, 255) # BGR 顺序
                cv2.putText(img, text_bot, (5, line_height * 2),
                            cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness, cv2.LINE_AA)

            out.write(img)

        out.release()
        print(f"--- [Video] Successfully saved to: {save_path} ---")

class MixedReplayBuffer:
    def __init__(self, device, agent_capacity=100000):
        self.device = device

        self.expert_frames = None # 存储所有单帧 (Total_Frames, 3, H, W)
        self.expert_goals = None
        self.expert_actions = None
        self.expert_rewards = None
        self.expert_dones = None

        self.expert_valid_indices = []
        self.expert_ptr = 0

        self.agent_frames = torch.empty((agent_capacity, 3, IMG_DIM_Y, IMG_DIM_X*2), dtype=torch.uint8, device=self.device)
        self.agent_goals = torch.empty((agent_capacity, 2), device=self.device)
        self.agent_actions = torch.empty((agent_capacity, 2), device=self.device)
        self.agent_rewards = torch.empty((agent_capacity, 1), device=self.device)
        self.agent_dones = torch.empty((agent_capacity, 1), device=self.device)

        self.agent_valid_indices = []
        self.agent_ptr = -1
        self.agent_size = 0
        self.agent_capacity = agent_capacity

        self.agent_episode_starts = torch.zeros(agent_capacity, dtype=torch.long, device=self.device)
        self.agent_curr_episode_start = 0

    def add_agent_experience(self, state, action, reward, done):
        self.agent_ptr = (self.agent_ptr + 1) % self.agent_capacity
        self.agent_size = min(self.agent_size + 1, self.agent_capacity)

        self.agent_frames[self.agent_ptr] = torch.from_numpy(state['visual'][-1]).permute(2, 0, 1).to(self.device)
        self.agent_goals[self.agent_ptr] = torch.from_numpy(state['goal']).to(self.device)
        self.agent_actions[self.agent_ptr] = torch.from_numpy(action).to(self.device)
        self.agent_rewards[self.agent_ptr] = torch.tensor([reward], device=self.device)
        self.agent_dones[self.agent_ptr] = torch.tensor([float(done)], device=self.device)

        self.agent_episode_starts[self.agent_ptr] = self.agent_curr_episode_start
        if done:
            self.agent_curr_episode_start = (self.agent_ptr + 1) % self.agent_capacity

    def clear_expert_data(self):
        self.expert_ptr = 0 # 只需要重置指针，不需要重新分配显存

    # 在 MixedReplayBuffer 类中增加
    def load_expert_data(self, expert_data_root):
        pkl_files = glob.glob(os.path.join(expert_data_root, "**/*.pkl"), recursive=True)
        
        # 1. 扫描阶段：加上进度条
        total_frames = 0
        # all_episodes = []
        for f_path in tqdm(pkl_files, desc="Scanning Expert Files"):
            with open(f_path, 'rb') as f:
                episode_data = pickle.load(f)
                total_frames += len(episode_data['visual_seq'])
                # all_episodes.append(episode_data)
        
        print(f"--- Detected total {total_frames} expert frames ---")
    
        # 2. 动态创建 Tensor (此步瞬间完成，不需要进度条)
        self.expert_frames = torch.empty((total_frames, 3, IMG_DIM_Y, IMG_DIM_X*2), dtype=torch.uint8, device=self.device)
        self.expert_goals = torch.empty((total_frames, 2), device=self.device)
        self.expert_actions = torch.empty((total_frames, 2), device=self.device)
        self.expert_rewards = torch.empty((total_frames, 1), device=self.device)
        self.expert_dones = torch.empty((total_frames, 1), device=self.device)

        self.expert_episode_starts = torch.zeros(total_frames, dtype=torch.long, device=self.device)

        # 3. 填充阶段：再加上进度条
        ptr = 0
        for f_path in tqdm(pkl_files, desc="Filling VRAM", unit="episode"):
            with open(f_path, 'rb') as f:
                ep = pickle.load(f)

            L_visual = len(ep['visual_seq'])
            L_action = len(ep['actions'])
            L = min(L_visual, L_action)
            
            # 存入图像 (L, H, W, 3) -> (L, 3, H, W)
            v_tensor = torch.from_numpy(ep['visual_seq'][:L]).permute(0, 3, 1, 2)
            self.expert_frames[ptr : ptr + L] = v_tensor.to(self.device)
            
            # 存入其他
            self.expert_goals[ptr : ptr + L] = torch.from_numpy(ep['goal_seq'][:L]).to(self.device)
            self.expert_actions[ptr : ptr + L] = torch.from_numpy(ep['actions'][:L]).to(self.device)
            self.expert_rewards[ptr : ptr + L] = torch.from_numpy(ep['rewards'][:L]).to(self.device).unsqueeze(1)
            if 'dones' in ep:
                d_tensor = torch.from_numpy(ep['dones'][:L]).float()
            else:
                # 如果没存 dones，最后一帧设为 1，其他为 0
                d_tensor = torch.zeros(L)
                d_tensor[-1] = 1.0
            self.expert_dones[ptr : ptr + L] = d_tensor.to(self.device).unsqueeze(1)
            self.expert_episode_starts[ptr : ptr + L] = ptr
            for i in range(L - 1):
                self.expert_valid_indices.append({
                    'curr': ptr + i,
                    'next': ptr + i + 1,
                    'start': ptr
                })
            ptr += L
        
        self.expert_ptr = len(self.expert_valid_indices)
        print(f"--- Expert Loaded into VRAM, Size: {self.expert_ptr} ---")

    def _get_stack(self, pool, starts_pool, global_ptr, stack_num=4):
        """通用堆叠函数，支持 Expert 和 Agent"""
        start_ptr = starts_pool[global_ptr]
        frames = []
        for i in range(stack_num):
            if pool is self.agent_frames:
                # 简单处理：在循环缓冲区中，如果还没存满就出界了，强行回正
                idx = (global_ptr - i) if (global_ptr - i) >= start_ptr else start_ptr
                idx = idx % self.agent_capacity
            else:
                idx = max(start_ptr, global_ptr - i)
            
            frames.append(pool[idx])
        return torch.cat(frames, dim=0)

    def sample(self, e_batch_size, a_batch_size):
        e_s, e_act, e_rew, e_done, e_ns = self.sample_expert(e_batch_size)
        a_s, a_act, a_rew, a_done, a_ns = self.sample_agent(a_batch_size)

        return (
            {
                'visual': self.finalize(a_s['visual'], e_s['visual'], True),
                'goal': self.finalize(a_s['goal'], e_s['goal'])
            },
            self.finalize(a_act, e_act),
            self.finalize(a_rew, e_rew),
            {
                'visual': self.finalize(a_ns['visual'], e_ns['visual'], True),
                'goal': self.finalize(a_ns['goal'], e_ns['goal'])
            },
            self.finalize(a_done, e_done)
        )
    
    def sample_expert(self, e_batch_size):
        sampled_train_idx = random.sample(list(self.train_indices), e_batch_size)
        # 获取真正的样本对象
        e_samples = [self.expert_valid_indices[i] for i in sampled_train_idx]
        e_v = torch.stack([self._get_stack(self.expert_frames, self.expert_episode_starts, s['curr']) for s in e_samples]).float()
        e_nv = torch.stack([self._get_stack(self.expert_frames, self.expert_episode_starts, s['next']) for s in e_samples]).float()

        e_indices_tensor = torch.tensor([s['curr'] for s in e_samples], device=self.device)
        e_next_indices_tensor = torch.tensor([s['next'] for s in e_samples], device=self.device)
        
        e_g = self.expert_goals[e_indices_tensor]
        e_act = self.expert_actions[e_indices_tensor]
        e_rew = self.expert_rewards[e_indices_tensor]
        e_done = self.expert_dones[e_indices_tensor]
        e_ng = self.expert_goals[e_next_indices_tensor]

        return {'visual': e_v, 'goal': e_g}, e_act, e_rew, e_done, {'visual': e_nv, 'goal': e_ng}
    
    def sample_agent(self, a_batch_size):
        a_samples = random.sample(range(self.agent_size - 1), a_batch_size)
        
        a_v = torch.stack([self._get_stack(self.agent_frames, self.agent_episode_starts, idx) for idx in a_samples])
        a_nv = torch.stack([self._get_stack(self.agent_frames, self.agent_episode_starts, idx+1) for idx in a_samples])

        a_indices_tensor = torch.tensor(a_samples, device=self.device)

        a_g = self.agent_goals[a_indices_tensor]
        a_act = self.agent_actions[a_indices_tensor]
        a_rew = self.agent_rewards[a_indices_tensor]
        a_done = self.agent_dones[a_indices_tensor]
        a_ng = self.agent_goals[(a_indices_tensor + 1) % self.agent_capacity]

        return {'visual': a_v, 'goal': a_g}, a_act, a_rew, a_done, {'visual': a_nv, 'goal': a_ng}
    
    def finalize(self, agent_tensor, expert_tensor, is_image=False):
            merged = torch.cat([agent_tensor.float(), expert_tensor.float()], dim=0)
            return merged / 255.0 if is_image else merged
    
    def get_val_loader(self, batch_size=32):
        # 使用自定义 Dataset，只有在 DataLoader 抽样时才进行堆叠计算
        dataset = ExpertValDataset(self, self.val_indices)
        return DataLoader(dataset, batch_size=batch_size, shuffle=False, num_workers=0)
    
    def split_expert_data(self, val_ratio=0.1):
        num_samples = len(self.expert_valid_indices) # 样本数
        all_indices = np.arange(num_samples)
        np.random.shuffle(all_indices)
        
        val_size = int(num_samples * val_ratio)
        # 这里的索引其实是 self.expert_valid_indices 的下标
        self.val_indices = all_indices[:val_size]
        self.train_indices = all_indices[val_size:]

class ExpertValDataset(Dataset):
    def __init__(self, buffer, indices):
        self.buffer = buffer
        self.indices = indices

    def __len__(self):
        return len(self.indices)

    def __getitem__(self, idx):
        # 拿到对应的全局专家索引
        global_idx = self.indices[idx]
        
        # 实时从 buffer 的大长条里切出 4 帧堆叠
        # 注意：这里的 global_idx 对应的是 valid_indices 里的位置
        v_stack = self.buffer._get_stack(self.buffer.expert_frames, 
                                        self.buffer.expert_episode_starts, 
                                        global_idx)
        
        # 归一化并获取其他数据
        v_stack = v_stack.float() / 255.0
        goal = self.buffer.expert_goals[global_idx]
        action = self.buffer.expert_actions[global_idx]
        
        return v_stack, goal, action