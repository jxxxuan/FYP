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

class ActorHead(nn.Module):
    def __init__(self, action_dim, embed_dim=256):
        super().__init__()
        # Input: 256-dim output from ViT + 2-dim goal vector = 258-dim
        self.fc = nn.Sequential(
            nn.Linear(embed_dim + 2, 256),
            nn.ReLU(),
            nn.Linear(256, 256),
            nn.ReLU()
        )
        self.mu = nn.Linear(256, action_dim)
        self.sigma = nn.Linear(256, action_dim)

    def forward(self, feature_vector, goal):
        x = torch.cat([feature_vector, goal], dim=-1)
        x = self.fc(x)
        return torch.tanh(self.mu(x)), F.softplus(self.sigma(x))

class CriticHead(nn.Module):
    def __init__(self, action_dim, embed_dim=256):
        super().__init__()
        # 256-dim feature + 2-dim goal + action_dim
        self.fc = nn.Sequential(
            nn.Linear(embed_dim + 2 + action_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 256),
            nn.ReLU(),
            nn.Linear(256, 1)
        )

    def forward(self, feature_vector, goal, action):
        x = torch.cat([feature_vector, goal, action], dim=-1)
        return self.fc(x)
    
class SharedViTSAC(nn.Module):
    def __init__(self, vit_encoder, action_dim):
        super().__init__()
        self.vit = vit_encoder  # The single visual encoder
        self.actor = ActorHead(action_dim)
        self.critic1 = CriticHead(action_dim)
        self.critic2 = CriticHead(action_dim)

    def get_feature(self, obs):
        return self.vit(obs) # Extract features once, shared across heads

class Actor(nn.Module):
    def __init__(self, vit_encoder, action_dim):
        super(Actor, self).__init__()
        self.vit = vit_encoder 
        
        # Three-layer MLP mentioned in paper (258 = 256-dim feature + 2-dim goal vector)
        self.fc1 = nn.Linear(258, 128)
        self.fc2 = nn.Linear(128, 32)
        
        self.mu_head = nn.Linear(32, action_dim)
        self.sigma_head = nn.Linear(32, action_dim)

    def forward(self, visual_obs, goal_vector):
        # 4. Extract features via ViT
        h_t = self.vit(visual_obs)  # Get 256-dim features
        
        # 5. Concatenate 2-dim goal vector -> 258-dim
        d_t = torch.cat([h_t, goal_vector], dim=-1) 
        
        # 6. Subsequent linear layers
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
        self.vit = vit_encoder  # Shared or independent ViT feature extractor 
        
        # Input dim = 256 (ViT output) + 2 (goal vector) + action_dim (action)
        input_dim = 256 + 2 + action_dim
        
        # MLP architecture mentioned in paper
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
        # Instantiate two independent Q-networks with different ViT instances
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
        # Store in list, dynamic growth, convert to numpy/tensor and save to disk after task completion
        self.visual_pool = []
        self.goal_pool = []
        self.action_pool = []
        self.reward_pool = []
        self.speed_pool = []
        self.debug_frame_pool = []
        self.terminate_reason = "Unknown"
        self.ptr = -1

    def add(self, visual, goal, action=None, reward=None, speed=None, terminate_reason = None, debug_frame=None):
        self.visual_pool.append(visual) # uint8 (H, W, 3)
        self.goal_pool.append(goal)     # float (2,)
        if action is not None: self.action_pool.append(action)
        if reward is not None: self.reward_pool.append(reward)
        if speed is not None: self.speed_pool.append(speed)
        if debug_frame is not None: self.debug_frame_pool.append(debug_frame)
        if terminate_reason is not None: self.terminate_reason = terminate_reason
        self.ptr += 1

    def get_current_obs(self):
        """
        Provide stacked observations at current step for RL training
        """
        start_idx = max(0, self.ptr - self.stack + 1)
        # Get the nearest N frames of visual input
        v_frames = self.visual_pool[start_idx : self.ptr + 1]
        # Get the latest 1 goal vector (goals usually don't need stacking)
        curr_goal = self.goal_pool[self.ptr]

        # Padding logic
        if len(v_frames) < self.stack:
            padding = [v_frames[0]] * (self.stack - len(v_frames))
            v_frames = padding + v_frames
            
        return {
            "visual": np.array(v_frames, dtype=np.uint8), # (4, H, W, 3)
            "goal": np.array(curr_goal, dtype=np.float32)
        }

    def pack_episode(self):
        """
        Compress entire Episode into a compact dictionary and save directly to pkl
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

        # 1. Get dimension (H, W*2)
        height, width, _ = video_source[0].shape
        size = (width, height)

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(save_path, fourcc, FPS, size)

        if width < 500:
            font_scale = 0.25 
            line_height = 8
            bg_width = int(width * 0.75)
        else:
            font_scale = 0.7
            line_height = 35
            bg_width = 550

        thickness = 1
        total_reward = 0
        # Iterate through the linear pool of the entire Episode
        for i in range(len(video_source)):
            # Convert and ensure uint8 format
            img = video_source[i].astype(np.uint8)

            curr_step_reward = self.reward_pool[i] if i < len(self.reward_pool) else 0.0
            curr_step_speed = self.speed_pool[i] if i < len(self.speed_pool) else 0.0
            total_reward += curr_step_reward

            curr_speed = self.speed_pool[i] if i < len(self.speed_pool) else 0.0

            # Draw a black background box on top-left of the screen to ensure readable text
            if use_debug:
                overlay = img.copy()
                cv2.rectangle(overlay, (0, 0), (bg_width, line_height * 2 + 5), (0, 0, 0), -1)
                cv2.addWeighted(overlay, 0.5, img, 0.5, 0, img)

            curr_goal = self.goal_pool[i]
            text_top = f"S: {i} | G:[{curr_goal[0]:.0f},{curr_goal[1]:.0f}] | V: {curr_step_speed:.1f}"
            cv2.putText(img, text_top, (5, line_height), 
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)

            text_bot = f"R: {curr_step_reward:.2f} | TR: {total_reward:.1f}"
            if i == len(video_source) - 1:
                text_bot += f" | END: {self.terminate_reason}"
                # Color logic: color changes based on termination reason, or keep red as reminder
                color = (0, 255, 0) if "R" == self.terminate_reason else (0, 0, 255)
            else:
                color = (0, 255, 0) if curr_step_reward >= 0 else (0, 0, 255)

            # Draw unified at line_height * 2 position
            cv2.putText(img, text_bot, (5, line_height * 2), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness, cv2.LINE_AA)
            out.write(img)

        for _ in range(FPS * 2): # Freeze for 2 seconds
            out.write(img) # The img here is the last frame

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
        self.agent_frames = torch.empty((self.agent_capacity, 3, IMG_DIM_Y, IMG_DIM_X * NUM_CAM), dtype=torch.uint8, device=self.device)
        self.agent_goals = torch.empty((self.agent_capacity, 2), device=self.device)
        self.agent_actions = torch.empty((self.agent_capacity, 2), device=self.device)
        self.agent_rewards = torch.empty((self.agent_capacity, 1), device=self.device)
        self.agent_dones = torch.empty((self.agent_capacity, 1), device=self.device)

        self._valid_set = set()  # Use set instead of list
        self.agent_ptr = -1
        self.agent_size = 0

        self.agent_episode_starts = torch.zeros(self.agent_capacity, dtype=torch.long, device=self.device)
        self.agent_curr_episode_start = 0

    def add_agent_experience(self, state, action, reward, done):
        self.agent_ptr = (self.agent_ptr + 1) % self.agent_capacity

        # Buffer is full, clean up valid_indices related to overwritten positions
        if self.agent_size == self.agent_capacity:
            # 1. Overwritten position itself
            if self.agent_ptr in self._valid_set:
                self._valid_set.discard(self.agent_ptr)

            # 2. Previous position of the overwritten position, as its next is about to be invalid
            prev_of_overwritten = (self.agent_ptr - 1) % self.agent_capacity
            if prev_of_overwritten in self._valid_set:
                self._valid_set.discard(prev_of_overwritten)

        # Write data
        self.agent_frames[self.agent_ptr] = torch.from_numpy(state['visual'][-1]).permute(2, 0, 1).to(self.device)
        self.agent_goals[self.agent_ptr] = torch.from_numpy(state['goal']).to(self.device)
        self.agent_actions[self.agent_ptr] = action.detach()
        self.agent_rewards[self.agent_ptr] = torch.tensor([reward], device=self.device)
        self.agent_dones[self.agent_ptr] = torch.tensor([float(done)], device=self.device)
        self.agent_episode_starts[self.agent_ptr] = self.agent_curr_episode_start

        # If previous frame is not done, then previous frame has a valid next (which is current frame)
        if self.agent_size > 0:
            prev_ptr = (self.agent_ptr - 1) % self.agent_capacity
            if self.agent_dones[prev_ptr] == 0:
                self._valid_set.add(prev_ptr)  # set add/discard are O(1)

        self.agent_size = min(self.agent_size + 1, self.agent_capacity)

        if done:
            self.agent_curr_episode_start = (self.agent_ptr + 1) % self.agent_capacity

    def clear_expert_data(self):
        self.expert_ptr = 0 # Only need to reset pointer, no need to reallocate VRAM

    def scan_frames(self, pkl_files):
        # 1. Scanning phase: with progress bar
        total_frames = 0
        for f_path in tqdm(pkl_files, desc="Scanning Expert Files"):
            with open(f_path, 'rb') as f:
                episode_data = pickle.load(f)
                total_frames += len(episode_data['visual_seq'])
        
        print(f"--- Detected total {total_frames} expert frames ---")
        return total_frames

    # Added to MixedReplayBuffer class
    def load_expert_data(self):
        pkl_files = glob.glob(os.path.join(ED_DIR, "**/*.pkl"), recursive=True)
        total_frames = self.scan_frames(pkl_files)
    
        # 2. Dynamically create Tensor (instantaneous, no progress bar needed)
        self.expert_frames = torch.empty((total_frames, 3, IMG_DIM_Y, IMG_DIM_X*NUM_CAM), dtype=torch.uint8, device=self.device)
        self.expert_goals = torch.empty((total_frames, 2), device=self.device)
        self.expert_actions = torch.empty((total_frames, 2), device=self.device)
        self.expert_rewards = torch.empty((total_frames, 1), device=self.device)
        self.expert_dones = torch.empty((total_frames, 1), device=self.device)

        self.expert_episode_starts = torch.zeros(total_frames, dtype=torch.long, device=self.device)

        # 3. Filling phase: with progress bar
        ptr = 0
        for f_path in tqdm(pkl_files, desc="Filling VRAM", unit="episode"):
            with open(f_path, 'rb') as f:
                ep = pickle.load(f)

            L_visual = len(ep['visual_seq'])
            L_action = len(ep['actions'])
            L = min(L_visual, L_action)
            
            # Store image (L, H, W, 3) -> (L, 3, H, W)
            v_tensor = torch.from_numpy(ep['visual_seq'][:L]).permute(0, 3, 1, 2)
            self.expert_frames[ptr : ptr + L] = v_tensor.to(self.device)
            
            # Store other variables
            self.expert_goals[ptr : ptr + L] = torch.from_numpy(ep['goal_seq'][:L]).to(self.device)
            self.expert_actions[ptr : ptr + L] = torch.from_numpy(ep['actions'][:L]).to(self.device)
            self.expert_rewards[ptr : ptr + L] = torch.from_numpy(ep['rewards'][:L]).to(self.device).unsqueeze(1)
            if 'dones' in ep:
                d_tensor = torch.from_numpy(ep['dones'][:L]).float()
            else:
                # If dones is not saved, set the last frame to 1, others to 0
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
        e_samples = random.sample(self.expert_valid_indices, e_batch_size)
        
        curr_indices = torch.tensor([s['curr'] for s in e_samples], dtype=torch.long, device=self.device)
        next_indices = torch.tensor([s['next'] for s in e_samples], dtype=torch.long, device=self.device)
        starts = torch.tensor([s['start'] for s in e_samples], dtype=torch.long, device=self.device)

        offsets = torch.arange(self.stack, device=self.device)
        
        # curr stack
        all_idx = (curr_indices.unsqueeze(1) - offsets.unsqueeze(0)).clamp(min=0)
        all_starts = self.expert_episode_starts[all_idx]
        same_ep = (all_starts == starts.unsqueeze(1))
        pad_idx = curr_indices.unsqueeze(1).expand_as(all_idx)
        final_idx = torch.where(same_ep, all_idx, pad_idx)
        B, S = final_idx.shape
        e_v = self.expert_frames[final_idx.view(-1)].view(B, S * 3, IMG_DIM_Y, IMG_DIM_X * NUM_CAM).float()

        # next stack
        next_all_idx = (next_indices.unsqueeze(1) - offsets.unsqueeze(0)).clamp(min=0)
        next_all_starts = self.expert_episode_starts[next_all_idx]
        next_same_ep = (next_all_starts == starts.unsqueeze(1))
        next_pad_idx = next_indices.unsqueeze(1).expand_as(next_all_idx)
        next_final_idx = torch.where(next_same_ep, next_all_idx, next_pad_idx)
        e_nv = self.expert_frames[next_final_idx.view(-1)].view(B, S * 3, IMG_DIM_Y, IMG_DIM_X * NUM_CAM).float()

        e_g = self.expert_goals[curr_indices]
        e_act = self.expert_actions[curr_indices]
        e_rew = self.expert_rewards[curr_indices]
        e_done = self.expert_dones[curr_indices]
        e_ng = self.expert_goals[next_indices]

        return {'visual': e_v, 'goal': e_g}, e_act, e_rew, e_done, {'visual': e_nv, 'goal': e_ng}
    
    def sample_agent(self, a_batch_size):
        sampled_indices = torch.tensor(
            random.sample(list(self._valid_set), a_batch_size), 
            dtype=torch.long, device=self.device
        )

        starts = self.agent_episode_starts[sampled_indices]  # (B,)
        # Batch construct stack indices
        offsets = torch.arange(self.stack, device=self.device)  # (4,)
        all_idx = (sampled_indices.unsqueeze(1) - offsets.unsqueeze(0)) % self.agent_capacity  # (B, 4)
        # Batch determine if in same episode
        all_starts = self.agent_episode_starts[all_idx]  # (B, 4)
        same_ep = (all_starts == starts.unsqueeze(1))  # (B, 4)
        pad_idx = sampled_indices.unsqueeze(1).expand_as(all_idx)  # (B, 4)
        final_idx = torch.where(same_ep, all_idx, pad_idx)  # (B, 4)

        B, S = final_idx.shape
        a_v = self.agent_frames[final_idx.view(-1)].view(B, S * 3, IMG_DIM_Y, IMG_DIM_X * NUM_CAM).float()

        next_indices = (sampled_indices + 1) % self.agent_capacity
        next_starts = self.agent_episode_starts[next_indices]
        next_all_idx = (next_indices.unsqueeze(1) - offsets.unsqueeze(0)) % self.agent_capacity
        next_all_starts = self.agent_episode_starts[next_all_idx]
        next_same_ep = (next_all_starts == next_starts.unsqueeze(1))
        next_pad_idx = next_indices.unsqueeze(1).expand_as(next_all_idx)
        next_final_idx = torch.where(next_same_ep, next_all_idx, next_pad_idx)
        a_nv = self.agent_frames[next_final_idx.view(-1)].view(B, S * 3, IMG_DIM_Y, IMG_DIM_X * NUM_CAM).float()
        
        a_g = self.agent_goals[sampled_indices]
        a_act = self.agent_actions[sampled_indices]
        a_rew = self.agent_rewards[sampled_indices]
        a_done = self.agent_dones[sampled_indices]
        a_ng = self.agent_goals[next_indices]

        return {'visual': a_v, 'goal': a_g}, a_act, a_rew, a_done, {'visual': a_nv, 'goal': a_ng}
    
    def finalize(self, agent_tensor, expert_tensor, is_image=False):
            merged = torch.cat([agent_tensor.float(), expert_tensor.float()], dim=0)
            return merged / 255.0 if is_image else merged
    
    def save_agent_buffer(self, episode):
        timestamp = time.strftime("%m%d-%H%M")
        filename = os.path.join(AG_DIR, f"ep{episode}_{timestamp}.pkl")

        # 1. Save current latest Buffer first
        data = {
            'agent_frames': self.agent_frames.cpu(),
            'agent_goals': self.agent_goals.cpu(),
            'agent_actions': self.agent_actions.cpu(),
            'agent_rewards': self.agent_rewards.cpu(),
            'agent_dones': self.agent_dones.cpu(),
            'agent_episode_starts': self.agent_episode_starts.cpu(),
            'agent_ptr': self.agent_ptr,
            'agent_size': self.agent_size,
            'valid_set': self._valid_set,
            'agent_curr_episode_start': self.agent_curr_episode_start
        }
        
        # Save first to ensure progress is saved even if subsequent deletion fails
        with open(filename, 'wb') as f:
            pickle.dump(data, f)
        print(f"--- Buffer Saved: {filename} ---")

        # 2. Cleanup logic: only keep the latest 2
        # Get all pkl files
        old_files = glob.glob(os.path.join(AG_DIR, "*.pkl"))
        
        # Sort old files by modification time (mtime) from newest to oldest
        old_files.sort(key=os.path.getmtime, reverse=True)

        # If number of files exceeds 2, delete the rest
        if len(old_files) > 2:
            files_to_delete = old_files[2:]
            for f in files_to_delete:
                try:
                    os.remove(f)
                    # print(f"--- Removed old buffer: {os.path.basename(f)} ---")
                except Exception as e:
                    print(f"--- Error deleting {f}: {e} ---")

    def load_agent_buffer(self):
        ckpt_files = glob.glob(os.path.join(AG_DIR, "*.pkl"))
    
        if not ckpt_files:
            print("--- No Checkpoint file ---")
            return 0, 0

        # 2. Define helper function to extract episode number from filename
        # Assume filename format is sac_carla_ep150_...
        def extract_episode(filename):
            match = re.search(r'ep(\d+)', filename)
            return int(match.group(1)) if match else -1

        # 3. Find file with the maximum episode number
        latest_pkl = max(ckpt_files, key=extract_episode)
        max_ep = extract_episode(latest_pkl)

        if max_ep == -1:
            print("--- Filename format mismatch (no 'ep' number found), please check filename ---")
            return 0, 0

        # 4. Execute loading logic
        print(f"--- Loading Agent Replay Buffer from {latest_pkl} ---")
        with open(latest_pkl, 'rb') as f:
            data = pickle.load(f)

        size = data['agent_size']
        # Move data back to GPU memory
        self.agent_frames.copy_(data['agent_frames'])   # Copy directly from CPU to existing GPU tensor without using .to(device)
        self.agent_goals.copy_(data['agent_goals'])
        self.agent_actions.copy_(data['agent_actions'])
        self.agent_rewards.copy_(data['agent_rewards'])
        self.agent_dones.copy_(data['agent_dones'])
        self.agent_episode_starts.copy_(data['agent_episode_starts'])

        self.agent_ptr = data['agent_ptr']
        self.agent_size = size
        self._valid_set = data.get('valid_set', set())
        self.agent_curr_episode_start = data['agent_curr_episode_start']
        
        print(f"--- Buffer Loaded: {self.agent_size} samples restored ---")
        return True