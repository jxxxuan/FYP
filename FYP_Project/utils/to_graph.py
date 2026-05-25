import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from constants import *

# 设置学术风格
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'serif'

def export_train_result(path, reward_ylim=(-50,50), alpha_ylim=(0,0.2), closs_ylim=(0,100), aloss_ylim=(0,50)):
    # 读取数据
    df = pd.read_csv(os.path.join(path,"train_log.csv")) 
    df = df.drop_duplicates(subset=['episode'], keep='last').sort_values('episode')

    # 通用平滑窗口
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

def export_test_result(path):
    # 1. 读取测试数据
    df_test = pd.read_csv(os.path.join(path,"test_log.csv"))

    # 确保按 episode 排序并剔除重复项
    df_test = df_test.drop_duplicates(subset=['episode'], keep='last').sort_values('episode')
    df_test['avg_reward_smooth'] = df_test['avg_reward'].rolling(window=3, min_periods=1, center=True).mean()
    # 2. 创建画布
    plt.figure(figsize=(10, 6))

    # 绘制折线图和散点
    plt.scatter(df_test['episode'], df_test['avg_reward'], color='green', alpha=0.3, label='Raw Test Reward')
    plt.plot(df_test['episode'], df_test['avg_reward_smooth'], color='darkgreen', linewidth=2, label='Smoothed Test Trend (W=3)')

    # 3. 寻找并标注表现最好的模型 (Best Checkpoint)
    best_row = df_test.loc[df_test['avg_reward'].idxmax()]
    plt.annotate(f"Best: {best_row['avg_reward']:.2f} (Ep {int(best_row['episode'])})",
             xy=(best_row['episode'], best_row['avg_reward']),
             # 将 +20 改为 +5 甚至更小，视视觉效果而定
             xytext=(best_row['episode']-1000, best_row['avg_reward'] + 5), 
             arrowprops=dict(facecolor='black', shrink=0.05),
             fontsize=12, fontweight='bold', color='darkred')

    # 4. 装饰图表
    plt.title('Test Performance across Checkpoints (Town04)', fontsize=14)
    plt.xlabel('Training Episode', fontsize=12)
    plt.ylabel('Average Reward (100 Trials)', fontsize=12)
    plt.axhline(y=0, color='black', linestyle='--', alpha=0.3) # 零分基准线
    plt.legend()
    plt.grid(True, which='both', linestyle='--', alpha=0.5)

    # 5. 保存用于 Report
    plt.tight_layout()
    plt.savefig(os.path.join(path,"test_performance_graph.png"), dpi=300)

if __name__ == "__main__":
    # export_train_result(r"G:\My Drive\FYP\Exp11\logs", reward_ylim=(-30,10), alpha_ylim=(0,0.2), closs_ylim=(-10,40), aloss_ylim=(-50,70))
    export_test_result(r"G:\My Drive\FYP\Exp11\logs")