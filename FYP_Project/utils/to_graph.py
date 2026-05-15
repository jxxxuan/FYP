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

def export_train_result(show=True):
    # 1. 读取数据
    df = pd.read_csv(r"G:\\My Drive\\FYP\\Exp1\\logs\\train_log.csv") 

    # 处理重叠
    df = df.drop_duplicates(subset=['episode'], keep='last').sort_values('episode')

    # 创建 2x2 画板
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))

    # --- 图1：累计奖励 (Cumulative Reward) ---
    df['reward_smooth'] = df['reward'].ewm(alpha=1-0.99, adjust=False).mean()
    ax1.plot(df['episode'], df['reward'], alpha=0.3, color='blue', label='Raw')
    ax1.plot(df['episode'], df['reward_smooth'], color='blue', linewidth=2, label='EMA 0.99')
    ax1.set_title('Cumulative Reward')
    ax1.set_ylabel('Reward')
    ax1.legend()

    # --- 图2：温度参数 (Alpha) ---
    ax2.plot(df['episode'], df['alpha'], color='red', linewidth=2)
    ax2.set_title('Alpha Adaptation (Entropy)')
    ax2.set_ylabel('Alpha')

    # --- 图3：Critic Loss (Value Network) ---
    # Loss 通常抖动很大，也建议做一点平滑处理
    df['critic_smooth'] = df['critic_loss'].rolling(window=50, min_periods=1).mean()
    ax3.plot(df['episode'], df['critic_loss'], alpha=0.3, color='orange')
    ax3.plot(df['episode'], df['critic_smooth'], color='orange', linewidth=2)
    ax3.set_title('Critic Loss')
    ax3.set_ylabel('Loss')
    ax3.set_xlabel('Episodes')

    # --- 图4：Actor Loss (Policy Network) ---
    df['actor_smooth'] = df['actor_loss'].rolling(window=50, min_periods=1).mean()
    ax4.plot(df['episode'], df['actor_loss'], alpha=0.3, color='green')
    ax4.plot(df['episode'], df['actor_smooth'], color='green', linewidth=2)
    ax4.set_title('Actor Loss')
    ax4.set_ylabel('Loss')
    ax4.set_xlabel('Episodes')

    plt.tight_layout()
    plt.savefig("G:\\My Drive\\FYP\Exp1\\logs\\train_full_metrics.png", dpi=300)
    if show:
        plt.show()

def export_test_result(show=True):
    # 1. 读取测试数据
    df_test = pd.read_csv(r"G:\\My Drive\\FYP\\Exp2\\logs\\test_log.csv")

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
                xytext=(best_row['episode']-500, best_row['avg_reward']+20),
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
    plt.savefig("G:\\My Drive\\FYP\\Exp2\\logs\\test_performance_graph.png", dpi=300)
    if show:
        plt.show()

if __name__ == "__main__":
    export_train_result(True)
    # export_test_result(False)