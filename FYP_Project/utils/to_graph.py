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

# 1. 读取数据
# df = pd.read_csv(TRAIN_LOG_DIR) 
# df = pd.read_csv(r"G:\\My Drive\\FYP\\Exp1\\logs\\train_log.csv") 

# # 处理重叠：如果 episode 有重复，保留最后一次出现的（即重启后的数据）
# df = df.drop_duplicates(subset=['episode'], keep='last').sort_values('episode')

# # 创建画板 (1行2列，分别画 Reward 和 Alpha)
# fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# # --- 图1：累计奖励 (Cumulative Reward) ---
# # 添加滑动平均 (Moving Average) 让曲线更平滑，方便观察收敛趋势
# df['reward_smooth'] = df['reward'].ewm(alpha=1-0.99, adjust=False).mean()
# ax1.plot(df['episode'], df['reward'], alpha=0.3, color='blue', label='Raw Reward')
# ax1.plot(df['episode'], df['reward_smooth'], color='blue', linewidth=2, label='Smoothed (EMA 0.99)')
# ax1.set_xlabel('Episodes')
# ax1.set_ylabel('Cumulative Reward')
# ax1.set_title('Training Reward Performance')
# ax1.legend()

# # --- 图2：温度参数 (Alpha) ---
# # 观察 Alpha 随分布变尖而减小的趋势
# ax2.plot(df['episode'], df['alpha'], color='red', linewidth=2)
# ax2.set_xlabel('Episodes')
# ax2.set_ylabel('Alpha (Temperature)')
# ax2.set_title('Alpha Adaptation')

# plt.tight_layout()
# # plt.savefig(TRAIN_GRAPH_DIR, dpi=300) # 保存高分辨率图用于 Report
# plt.savefig("G:\\My Drive\\FYP\Exp1\\logs\\train_graph.png", dpi=300) # 保存高分辨率图用于 Report
# plt.show()

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
plt.show()