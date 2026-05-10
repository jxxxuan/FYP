import random
import torch
import os
from envs.carla_env import CarlaEnv
from hyperparameter import *
from constants import *
from utils.utils import *
from bc import *
from start_carla import restart_carla
import glob
import re
import os
import torch
import shutil
from torch.utils.tensorboard import SummaryWriter

@torch.no_grad()
def test(env, target_town, tasks, junctions, actor, current_episode):
    tasks_in_town = tasks.get(target_town, [])
    if not tasks_in_town:
        return
    
    selected_task = random.choice(tasks_in_town)
    junction_name = selected_task['junction_name']
    junction_data = junctions[target_town].get('test_junctions', {}).get(junction_name, [])
    actual_actor = actor._orig_mod if hasattr(actor, "_orig_mod") else actor
    actual_actor.eval()
    
    timestamp = time.strftime("%m%d-%H%M")
    video_path = os.path.join(RC_DIR, f"debug_{target_town}_ep{current_episode}_{timestamp}.mp4")
    start, target = build_pose(selected_task)

    obs, _ = env.reset(target_town, level=0, junction_data=junction_data, start_transform=start, target_location=target, video_path=video_path)
    
    episode_reward = 0
    done = False
    step = 0
    
    while step < MAX_STEPS + (MAX_STEPS * 0.2) and not done:
        v_input, g_input = preprocess_obs(obs['visual'], obs['goal'], DEVICE)

        mu, _ = actual_actor(v_input, g_input)
        action = torch.tanh(mu)
        action_numpy = action.detach().cpu().numpy()[0]

        next_obs, reward, terminated, truncated, info = env.step(action_numpy)
        
        obs = next_obs
        episode_reward += reward
        step += 1
        done = terminated or truncated
            
    print(f"Test Run Reward: {episode_reward:.2f} | Steps: {step} | Reason: {info['reason']}")

    actual_actor.train()
    return episode_reward

def get_all_checkpoints():
    files = glob.glob(os.path.join(CP_DIR, "*.pth"))
    # 按 Episode 数字排序
    files.sort(key=lambda x: int(re.search(r'ep(\d+)', x).group(1)))
    return files

def batch_test_and_clean(env, test_tasks, junctions, writer):
    ckpt_list = get_all_checkpoints()
    print(f"--- 找到 {len(ckpt_list)} 个待测模型 ---")

    best_reward = -float('inf')
    best_ckpt = ""

    for ckpt_path in ckpt_list:
        ep_num = int(re.search(r'ep(\d+)', ckpt_path).group(1))
        
        print(f"\n>>> 正在测试 Episode {ep_num} ...")
        
        # 1. 加载权重
        try:
            models = load_checkpoint(ckpt_path, DEVICE)
        except Exception as e:
            print(f"加载失败 {ckpt_path}: {e}")
            continue

        # 2. 调用你现有的 test 函数
        # 注意：为了准确，可以多测几次取平均值
        total_test_reward = 0
        num_trials = 3 
        for _ in range(num_trials):
            reward = test(env, "Town04", test_tasks, junctions, models['actor'], ep_num)
            total_test_reward += reward
        
        avg_reward = total_test_reward / num_trials
        print(f"Episode {ep_num} 平均得分: {avg_reward:.2f}")

        # 3. 记录表现最好的模型
        if avg_reward > best_reward:
            best_reward = avg_reward
            best_ckpt = ckpt_path
        writer.add_scalar('Reward/Test', avg_reward, ep_num)

    # --- 清理逻辑 ---
    print("\n--- 测试完成，开始清理 ---")
    # 保留原则：保留表现最好的，以及最后生成的两个（防止意外）
    keep_files = {best_ckpt, ckpt_list[-1], ckpt_list[-2]}
    
    for ckpt_path in ckpt_list:
        if ckpt_path not in keep_files:
            try:
                os.remove(ckpt_path)
                print(f"已移除冗余模型: {os.path.basename(ckpt_path)}")
            except Exception as e:
                print(f"移除失败: {e}")

if __name__ == '__main__':
    with open(INTESECTION_JSON, 'r') as f:
        junctions = json.load(f)
    env = CarlaEnv()
    test_tasks, test_towns = get_task_info(TEST_JSON)
    writer = SummaryWriter(log_dir=LOG_DIR)
    batch_test_and_clean(env, test_tasks, junctions, writer)

        