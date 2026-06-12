import pickle
import glob
import os
import numpy as np
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from constants import ED_DIR

# Find all pkl files
pkl_files = glob.glob(os.path.join(ED_DIR, "**/*.pkl"), recursive=True)

if not pkl_files:
    print("Cannot find any pkl files, please check the path!")
else:
    print(f"Found {len(pkl_files)} files, starting sample check...\n")
    
    # Check the first 3 files
    for i in range(min(3, len(pkl_files))):
        f_path = pkl_files[i]
        with open(f_path, 'rb') as f:
            episode_data = pickle.load(f) # Directly loaded as a dictionary
        
            # Extract individual sequences
            visual = episode_data['visual_seq']
            goal = episode_data['goal_seq']
            actions = episode_data['actions']
            rewards = episode_data['rewards']
            
            n_visual = len(visual)
            n_action = len(actions)
            
            print(f"--- File: {os.path.basename(f_path)} ---")
            print(f"State count (Visual/Goal): {n_visual} | Shape: {visual.shape}")
            print(f"Action count (Actions):     {n_action} | Shape: {actions.shape}")
            print(f"Reward count (Rewards):     {len(rewards)}")
            
            if n_visual == n_action + 1:
                print("✅ State/Action alignment: matches (n+1) logic")
            else:
                print(f"❌ Abnormality in count: Visual({n_visual}) != Actions({n_action}) + 1")
                
            print(f"Data type check: {visual.dtype}, {actions.dtype}")
            print("-" * 40)