import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from constants import *

# Academic style settings
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'serif'

def export_train_result(path, reward_ylim=(-50,50), alpha_ylim=(0,0.2), closs_ylim=(0,100), aloss_ylim=(0,50), start_ep=None, end_ep=None):
    # Read data
    df = pd.read_csv(os.path.join(path,"train_log.csv")) 
    df = df.drop_duplicates(subset=['episode'], keep='last').sort_values('episode')

    # Filter episodes if limits are specified
    if start_ep is not None:
        df = df[df['episode'] >= start_ep]
    if end_ep is not None:
        df = df[df['episode'] <= end_ep]

    # Smoothing window
    SMOOTH_WINDOW = 100 

    # 1. Export Reward Curve
    plt.figure(figsize=(10, 6))
    df['reward_smooth'] = df['reward'].ewm(alpha=1-0.99, adjust=False).mean()
    plt.plot(df['episode'], df['reward'], alpha=0.3, color='#4C72B0', label='Raw Reward')
    plt.plot(df['episode'], df['reward_smooth'], color='#000080', linewidth=2, label='EMA 0.99')
    plt.title('Training Reward Performance', fontsize=14)
    plt.xlabel('Episodes'); plt.ylabel('Cumulative Reward'); plt.legend()
    plt.ylim(reward_ylim)
    plt.tight_layout()
    plt.savefig(os.path.join(path,"reward_curve.png"), dpi=300)
    plt.close()

    # 2. Export Alpha Curve
    plt.figure(figsize=(10, 6))
    plt.plot(df['episode'], df['alpha'], color='#C44E52', linewidth=2)
    plt.title('Alpha Adaptation (Entropy Coefficient)', fontsize=14)
    plt.xlabel('Episodes'); plt.ylabel('Alpha Value')
    plt.ylim(alpha_ylim)
    plt.tight_layout()
    plt.savefig(os.path.join(path,"alpha_curve.png"), dpi=300)
    plt.close()

    # 3. Export Critic Loss
    plt.figure(figsize=(10, 6))
    df['critic_smooth'] = df['critic_loss'].rolling(window=SMOOTH_WINDOW, min_periods=1).mean()
    plt.plot(df['episode'], df['critic_loss'], alpha=0.2, color='#8172B3')
    plt.plot(df['episode'], df['critic_smooth'], color='#4B0082', linewidth=2)
    plt.title('Critic Network Loss (Q-Value Convergence)', fontsize=14)
    plt.xlabel('Episodes'); plt.ylabel('MSE Loss')
    plt.ylim(closs_ylim)
    plt.tight_layout()
    plt.savefig(os.path.join(path,"critic_loss.png"), dpi=300)
    plt.close()

    # 4. Export Actor Loss
    plt.figure(figsize=(10, 6))
    df['actor_smooth'] = df['actor_loss'].rolling(window=SMOOTH_WINDOW, min_periods=1).mean()
    plt.plot(df['episode'], df['actor_loss'], alpha=0.2, color='#55A868')
    plt.plot(df['episode'], df['actor_smooth'], color='#006400', linewidth=2)
    plt.title('Actor Network Loss (Policy Improvement)', fontsize=14)
    plt.xlabel('Episodes'); plt.ylabel('Negative Q-Value')
    plt.ylim(aloss_ylim)
    plt.tight_layout()
    plt.savefig(os.path.join(path,"actor_loss.png"), dpi=300)
    plt.close()

def export_test_result(path, reward_ylim=(-50,50), start_ep=None, end_ep=None):
    # 1. Read test data
    df_test = pd.read_csv(os.path.join(path,"test_log.csv"))

    # Ensure sorting and remove duplicates
    df_test = df_test.drop_duplicates(subset=['episode'], keep='last').sort_values('episode')
    
    # Filter episodes if limits are specified
    if start_ep is not None:
        df_test = df_test[df_test['episode'] >= start_ep]
    if end_ep is not None:
        df_test = df_test[df_test['episode'] <= end_ep]

    df_test['avg_reward_smooth'] = df_test['avg_reward'].rolling(window=20, min_periods=1, center=True).mean()
    
    # 2. Create canvas
    plt.figure(figsize=(10, 6))

    # Plot graphs
    plt.scatter(df_test['episode'], df_test['avg_reward'], color='green', alpha=0.1, label='Raw Test Reward')
    plt.plot(df_test['episode'], df_test['avg_reward_smooth'], color='darkgreen', linewidth=2, label='Smoothed Test Trend (W=3)')

    # 3. Highlight best checkpoint
    # best_row = df_test.loc[df_test['avg_reward'].idxmax()]
    # plt.annotate(f"Best: {best_row['avg_reward']:.2f} (Ep {int(best_row['episode'])})",
    #          xy=(best_row['episode'], best_row['avg_reward']),
    #          xytext=(best_row['episode']-1000, best_row['avg_reward'] + 5), 
    #          arrowprops=dict(facecolor='black', shrink=0.05),
    #          fontsize=12, fontweight='bold', color='darkred')

    # 4. Decorate graph
    plt.title('Test Performance across Checkpoints (Town04)', fontsize=14)
    plt.xlabel('Training Episode', fontsize=12)
    plt.ylabel('Average Reward (100 Trials)', fontsize=12)
    plt.ylim(reward_ylim)
    plt.axhline(y=0, color='black', linestyle='--', alpha=0.3)
    plt.legend()
    plt.grid(True, which='both', linestyle='--', alpha=0.5)

    # 5. Save figure
    plt.tight_layout()
    plt.savefig(os.path.join(path,"test_performance_graph.png"), dpi=300)

if __name__ == "__main__":
    # Example: Filter episodes from 1000 to 5000
    export_test_result(r"G:\My Drive\FYP\Final1\logs", reward_ylim=(-7.5,15), start_ep=0, end_ep=112500)
    # export_train_result(r"G:\My Drive\FYP\Final1\logs", reward_ylim=(-7.5,15), alpha_ylim=(0,0.05), closs_ylim=(0,8), aloss_ylim=(-25,30), start_ep=0, end_ep=112500)