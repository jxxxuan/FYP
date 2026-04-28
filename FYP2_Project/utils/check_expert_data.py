import pickle
import glob
import os
import numpy as np
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from constants import ED_DIR

# 查找所有的 pkl 文件
pkl_files = glob.glob(os.path.join(ED_DIR, "**/*.pkl"), recursive=True)

if not pkl_files:
    print("找不到任何 pkl 文件，请检查路径！")
else:
    print(f"找到 {len(pkl_files)} 个文件，开始抽样检查...\n")
    
    # 检查前 3 个文件
    for i in range(min(3, len(pkl_files))):
        f_path = pkl_files[i]
        with open(f_path, 'rb') as f:
            episode_data = pickle.load(f) # 直接是一个字典
        
            # 提取各个序列
            visual = episode_data['visual_seq']
            goal = episode_data['goal_seq']
            actions = episode_data['actions']
            rewards = episode_data['rewards']
            
            n_visual = len(visual)
            n_action = len(actions)
            
            print(f"--- 文件: {os.path.basename(f_path)} ---")
            print(f"状态数 (Visual/Goal): {n_visual} | 形状: {visual.shape}")
            print(f"动作数 (Actions):     {n_action} | 形状: {actions.shape}")
            print(f"奖励数 (Rewards):     {len(rewards)}")
            
            if n_visual == n_action + 1:
                print("✅ 状态/动作数量对齐: 符合 (n+1) 逻辑")
            else:
                print(f"❌ 数量异常: Visual({n_visual}) != Actions({n_action}) + 1")
                
            print(f"数据类型检查: {visual.dtype}, {actions.dtype}")
            print("-" * 40)