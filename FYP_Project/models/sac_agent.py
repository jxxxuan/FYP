import random
import re
import time
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
from constants import *
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
        self.terminate_reason = "Unknown"
        self.ptr = -1

    def add(self, visual, goal, action=None, reward=None, terminate_reason = None, debug_frame=None):
        self.visual_pool.append(visual) # uint8 (H, W, 3)
        self.goal_pool.append(goal)     # float (2,)
        if action is not None: self.action_pool.append(action)
        if reward is not None: self.reward_pool.append(reward)
        if debug_frame is not None: self.debug_frame_pool.append(debug_frame)
        if terminate_reason is not None: self.terminate_reason = terminate_reason
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

    def pack_episode(self):
        """
        将整个 Episode 压缩成一个紧凑字典，直接传给 pkl
        """
        return {
            "visual_seq": np.array(self.visual_pool, dtype=np.uint8),
            "goal_seq": np.array(self.goal_pool, dtype=np.float32),
            "actions": np.array(self.action_pool, dtype=np.float32),
            "rewards": np.array(self.reward_pool, dtype=np.float32),
            "terminate_reason": self.terminate_reason
        }

    def to_video(self, save_path):
        use_debug = len(self.debug_frame_pool) > 0
        video_source = self.debug_frame_pool if use_debug else self.visual_pool

        if not video_source:
            print("Buffer is empty, nothing to save.")
            return

        # 1. 获取尺寸 (H, W*2)
        height, width, _ = video_source[0].shape
        size = (width, height)

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(save_path, fourcc, FPS, size)

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

            curr_step_reward = self.reward_pool[i] if i < len(self.reward_pool) else 0.0
            total_reward += curr_step_reward

            # 在画面左上角画个黑框背景，防止文字看不清
            overlay = img.copy()
            cv2.rectangle(overlay, (0, 0), (bg_width, line_height * 2 + 10), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.5, img, 0.5, 0, img)

            curr_goal = self.goal_pool[i]
            text_top = f"S: {i} | TR: {total_reward:.1f} | G:[{curr_goal[0]:.0f},{curr_goal[1]:.0f}]"
            cv2.putText(img, text_top, (5, line_height), 
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)

            text_bot = f"R: {curr_step_reward:.2f}"
            if i == len(video_source) - 1:
                text_bot += f" | END: {self.terminate_reason}"
                # 颜色逻辑：如果有结束原因，可以根据结果变色，或者保持红色提醒
                color = (0, 255, 0) if "R" == self.terminate_reason else (0, 0, 255)
            else:
                color = (0, 255, 0) if curr_step_reward >= 0 else (0, 0, 255)

            # 统一在 line_height * 2 的位置画出来
            cv2.putText(img, text_bot, (5, line_height * 2), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness, cv2.LINE_AA)
            out.write(img)

        for _ in range(FPS * 2): # 定格 2 秒
            out.write(img) # 这里的 img 是最后一帧

        out.release()
        print(f"--- [Video] Successfully saved to: {save_path} ---")

class MixedReplayBuffer:
    def __init__(self, device, agent_capacity=100000):
        self.device = device
        self.agent_capacity = agent_capacity

        self.expert_frames = None
        self.expert_goals = None
        self.expert_actions = None
        self.expert_rewards = None
        self.expert_dones = None

        self.expert_valid_indices = []
        self.expert_ptr = -1

        self.init_agent_buffer()

        self.stack = 4

    def init_agent_buffer(self):
        self.agent_frames = torch.empty((self.agent_capacity, 3, IMG_DIM_Y, IMG_DIM_X*2), dtype=torch.uint8, device=self.device)
        self.agent_goals = torch.empty((self.agent_capacity, 2), device=self.device)
        self.agent_actions = torch.empty((self.agent_capacity, 2), device=self.device)
        self.agent_rewards = torch.empty((self.agent_capacity, 1), device=self.device)
        self.agent_dones = torch.empty((self.agent_capacity, 1), device=self.device)

        self.agent_valid_indices = []
        self.agent_ptr = -1
        self.agent_size = 0
        self.agent_capacity = self.agent_capacity

        self.agent_episode_starts = torch.zeros(self.agent_capacity, dtype=torch.long, device=self.device)
        self.agent_curr_episode_start = 0

    def add_agent_experience(self, state, action, reward, done):
        self.agent_ptr = (self.agent_ptr + 1) % self.agent_capacity
        if self.agent_size == self.agent_capacity:
            if self.agent_ptr in self.agent_valid_indices:
                self.agent_valid_indices.remove(self.agent_ptr)

        self.agent_frames[self.agent_ptr] = torch.from_numpy(state['visual'][-1]).permute(2, 0, 1).to(self.device)
        self.agent_goals[self.agent_ptr] = torch.from_numpy(state['goal']).to(self.device)
        self.agent_actions[self.agent_ptr] = action.detach()
        self.agent_rewards[self.agent_ptr] = torch.tensor([reward], device=self.device)
        self.agent_dones[self.agent_ptr] = torch.tensor([float(done)], device=self.device)
        self.agent_episode_starts[self.agent_ptr] = self.agent_curr_episode_start

        if self.agent_size > 0:
            prev_ptr = (self.agent_ptr - 1) % self.agent_capacity
            # 如果上一步不是 done，说明 prev_ptr 和当前 agent_ptr 是连贯的
            if self.agent_dones[prev_ptr] == 0:
                self.agent_valid_indices.append(prev_ptr)

        self.agent_size = min(self.agent_size + 1, self.agent_capacity)
        if done:
            self.agent_curr_episode_start = (self.agent_ptr + 1) % self.agent_capacity

    def clear_expert_data(self):
        self.expert_ptr = 0 # 只需要重置指针，不需要重新分配显存

    def scan_frames(self, pkl_files):
        # 1. 扫描阶段：加上进度条
        total_frames = 0
        for f_path in tqdm(pkl_files, desc="Scanning Expert Files"):
            with open(f_path, 'rb') as f:
                episode_data = pickle.load(f)
                total_frames += len(episode_data['visual_seq'])
        
        print(f"--- Detected total {total_frames} expert frames ---")
        return total_frames

    # 在 MixedReplayBuffer 类中增加
    def load_expert_data(self):
        pkl_files = glob.glob(os.path.join(ED_DIR, "**/*.pkl"), recursive=True)
        total_frames = self.scan_frames(pkl_files)
    
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
            idx = max(start_ptr, global_ptr - i)
            if idx < 0: idx = 0
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
        # sampled_train_idx = random.sample(list(self.expert_valid_indices), e_batch_size)
        # 获取真正的样本对象
        # e_samples = [self.expert_valid_indices[i] for i in sampled_train_idx]
        e_samples = random.sample(self.expert_valid_indices, e_batch_size)
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
        sampled_indices = random.sample(self.agent_valid_indices, a_batch_size)
        
        a_v = torch.stack([self._get_stack(self.agent_frames, self.agent_episode_starts, idx) for idx in sampled_indices])
        a_nv = torch.stack([self._get_stack(self.agent_frames, self.agent_episode_starts, (idx + 1) % self.agent_capacity) for idx in sampled_indices])

        indices_tensor = torch.tensor(sampled_indices, device=self.device)
        next_indices_tensor = (indices_tensor + 1) % self.agent_capacity

        a_g = self.agent_goals[indices_tensor]
        a_act = self.agent_actions[indices_tensor]
        a_rew = self.agent_rewards[indices_tensor]
        a_done = self.agent_dones[indices_tensor]
        a_ng = self.agent_goals[next_indices_tensor]

        return {'visual': a_v, 'goal': a_g}, a_act, a_rew, a_done, {'visual': a_nv, 'goal': a_ng}
    
    def finalize(self, agent_tensor, expert_tensor, is_image=False):
            merged = torch.cat([agent_tensor.float(), expert_tensor.float()], dim=0)
            return merged / 255.0 if is_image else merged
    
    def save_agent_buffer(self, episode):
        timestamp = time.strftime("%m%d-%H%M")
        filename = os.path.join(AG_DIR, f"ep{episode}_{timestamp}.pkl")

        # 1. 先保存当前最新的 Buffer
        data = {
            'agent_frames': self.agent_frames.cpu(),
            'agent_goals': self.agent_goals.cpu(),
            'agent_actions': self.agent_actions.cpu(),
            'agent_rewards': self.agent_rewards.cpu(),
            'agent_dones': self.agent_dones.cpu(),
            'agent_episode_starts': self.agent_episode_starts.cpu(),
            'agent_ptr': self.agent_ptr,
            'agent_size': self.agent_size,
            'agent_valid_indices': self.agent_valid_indices,
            'agent_curr_episode_start': self.agent_curr_episode_start
        }
        
        # 先存，确保即便后续删除出错，当前的进度也保住了
        with open(filename, 'wb') as f:
            pickle.dump(data, f)
        print(f"--- Buffer Saved: {filename} ---")

        # 2. 清理逻辑：只保留最新的 2 个
        # 获取所有 pkl 文件
        old_files = glob.glob(os.path.join(AG_DIR, "*.pkl"))
        
        # 按文件的修改时间 (mtime) 从新到旧排序
        old_files.sort(key=os.path.getmtime, reverse=True)

        # 如果文件数量超过 2 个，删除剩下的
        if len(old_files) > 2:
            files_to_delete = old_files[2:]
            for f in files_to_delete:
                try:
                    os.remove(f)
                    # print(f"--- Removed old buffer: {os.path.basename(f)} ---")
                except Exception as e:
                    print(f"--- Error deleting {f}: {e} ---")

    def load_agent_buffer(self):
        """从硬盘读取数据并重新加载到显存"""
        if not os.path.exists(AG_DIR):
            print(f"--- No buffer found, starting fresh ---")
            return False
        
        ckpt_files = glob.glob(os.path.join(AG_DIR, "*.pkl"))
    
        if not ckpt_files:
            print("--- No Checkpoint file ---")
            return 0, 0

        # 2. 定义一个辅助函数，提取文件名里的 episode 数字
        # 假设你的文件名格式是 sac_carla_ep150_...
        def extract_episode(filename):
            match = re.search(r'ep(\d+)', filename)
            return int(match.group(1)) if match else -1

        # 3. 找到 episode 最大的那个文件
        latest_pkl = max(ckpt_files, key=extract_episode)
        max_ep = extract_episode(latest_pkl)

        if max_ep == -1:
            print("--- 文件名格式不匹配（未找到 'ep' 数字），请检查文件名 ---")
            return 0, 0

        # 4. 执行加载逻辑
        print(f"--- Loading Agent Replay Buffer from {latest_pkl} ---")
        with open(latest_pkl, 'rb') as f:
            data = pickle.load(f)

        size = data['agent_size']
        # 将数据搬回显存
        self.agent_frames.copy_(data['agent_frames'])   # 不经过 .to(device)，直接从 CPU 拷贝到已有的 GPU tensor
        self.agent_goals.copy_(data['agent_goals'])
        self.agent_actions.copy_(data['agent_actions'])
        self.agent_rewards.copy_(data['agent_rewards'])
        self.agent_dones.copy_(data['agent_dones'])
        self.agent_episode_starts.copy_(data['agent_episode_starts'])

        self.agent_ptr = data['agent_ptr']
        self.agent_size = size
        self.agent_valid_indices = data['agent_valid_indices']
        self.agent_curr_episode_start = data['agent_curr_episode_start']
        
        print(f"--- Buffer Loaded: {self.agent_size} samples restored ---")
        return True