import pickle
import glob
import os
import numpy as np
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from constants import ED_DIR, ED_N_DIR

# 查找所有的 pkl 文件
pkl_files = glob.glob(os.path.join(ED_N_DIR, "**/*.pkl"), recursive=True)

if not pkl_files:
    print("找不到任何 pkl 文件，请检查路径！")
else:
    print(f"找到 {len(pkl_files)} 个文件，开始抽样检查...\n")
    
    # 检查前 3 个文件
    for i in range(min(3, len(pkl_files))):
        f_path = pkl_files[i]
        with open(f_path, 'rb') as f:
            data = pickle.load(f) # 这是一个 list
            if len(data) > 0:
                first_step = data[0]
                visual = first_step['obs']['visual']
                goal = first_step['obs']['goal']
                action = first_step['action']
                
                print(f"--- 文件: {os.path.basename(f_path)} ---")
                print(f"图像形状 (visual): {np.array(visual).shape} | 类型: {np.array(visual).dtype}")
                print(f"目标形状 (goal):   {np.array(goal).shape}")
                print(f"动作形状 (action): {np.array(action).shape}")
                print(f"每回合步数: {len(data)}")
                print("-" * 30)