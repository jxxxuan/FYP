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
# def test(env, target_town, tasks, junctions, model, current_episode):
    tasks_in_town = tasks.get(target_town, [])
    if not tasks_in_town:
        return
    
    selected_task = random.choice(tasks_in_town)
    junction_name = selected_task['junction_name']
    junction_data = junctions[target_town].get('test_junctions', {}).get(junction_name, [])
    actual_actor = actor._orig_mod if hasattr(actor, "_orig_mod") else actor
    actual_actor.eval()
    # actual_model = model._orig_mod if hasattr(model, "_orig_mod") else model
    # actual_model.eval()
    
    timestamp = time.strftime("%H-%M-%S")
    video_path = os.path.join(RC_DIR, f"debug_{target_town}_ep{current_episode}_{timestamp}.mp4")
    start, target = build_pose(selected_task)

    obs, _ = env.reset(target_town, level=0, junction_data=junction_data, start_transform=start, target_location=target, video_path=video_path)
    
    episode_reward = 0
    done = False
    step = 0
    
    while step < MAX_STEPS + (MAX_STEPS * 0.2) and not done:
        v_input, g_input = preprocess_obs(obs['visual'], obs['goal'], DEVICE)

        mu, _ = actual_actor(v_input, g_input)
        # feat = actual_model.get_feature(v_input)
        # mu, _ = actual_model.actor(feat, g_input)
        action = torch.tanh(mu)
        action_numpy = action.detach().cpu().numpy()[0]

        next_obs, reward, terminated, truncated, info = env.step(action_numpy)
        
        obs = next_obs
        episode_reward += reward
        step += 1
        done = terminated or truncated
            
    print(f"Test Run Reward: {episode_reward:.2f} | Steps: {step} | Reason: {info['reason']}")

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
    best_ckpt = None

    for ckpt_path in ckpt_list:
        ep_num = int(re.search(r'ep(\d+)', ckpt_path).group(1))
        
        print(f"\n>>> 正在测试 Episode {ep_num} ...")
        
        # 1. 加载权重
        try:
            models = load_checkpoint(ckpt_path, DEVICE)
            # models = load_share_checkpoint(ckpt_path, DEVICE)
        except Exception as e:
            print(f"加载失败 {ckpt_path}: {e}")
            continue

        # 2. 调用你现有的 test 函数
        # 注意：为了准确，可以多测几次取平均值
        total_test_reward = 0
        num_trials = 5
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

    if best_ckpt is None:
        print("没有可用模型")
        return

    print(f"\n--- Best Model: {os.path.basename(best_ckpt)} | Avg Reward: {best_reward:.2f} ---")
    print("--- 开始 100 次详细评估 ---")

    models = load_checkpoint(best_ckpt, DEVICE)
    detailed_test(env, "Town04", test_tasks, junctions, models['actor'], writer, num_trials=100)
    
def detailed_test(env, target_town, tasks, junctions, model, writer, num_trials=100):
    actual_model = model._orig_mod if hasattr(model, "_orig_mod") else model
    actual_model.eval()

    results = {
        'reward': [],
        'steps': [],
        'reason': []
    }

    for trial in range(num_trials):
        tasks_in_town = tasks.get(target_town, [])
        if not tasks_in_town:
            break

        selected_task = random.choice(tasks_in_town)
        junction_name = selected_task['junction_name']
        junction_data = junctions[target_town].get('test_junctions', {}).get(junction_name, [])
        start, target = build_pose(selected_task)

        obs, _ = env.reset(target_town, level=0, junction_data=junction_data,
                           start_transform=start, target_location=target)

        episode_reward = 0
        step = 0
        done = False

        with torch.no_grad():
            while step < int(MAX_STEPS * 1.2) and not done:
                v_input, g_input = preprocess_obs(obs['visual'], obs['goal'], DEVICE)
                mu, _ = actual_model(v_input, g_input)
                action = torch.tanh(mu).detach().cpu().numpy()[0]

                obs, reward, terminated, truncated, info = env.step(action)
                episode_reward += reward
                step += 1
                done = terminated or truncated

        results['reward'].append(episode_reward)
        results['steps'].append(step)
        results['reason'].append(info['reason'])

        if (trial + 1) % 10 == 0:
            print(f"  Progress: {trial+1}/{num_trials}")

    # 统计
    reasons = results['reason']
    total = len(reasons)

    success_rate   = reasons.count('R')  / total * 100
    collision_rate = reasons.count('C')  / total * 100
    offroad_rate   = reasons.count('O')  / total * 100
    toofar_rate    = reasons.count('TF') / total * 100
    timeout_rate   = reasons.count('T')  / total * 100

    avg_reward = sum(results['reward']) / total
    avg_steps  = sum(results['steps'])  / total

    print(f"\n{'='*40}")
    print(f"  详细评估结果 ({total} 次)")
    print(f"{'='*40}")
    print(f"  平均 Reward   : {avg_reward:.2f}")
    print(f"  平均 Steps    : {avg_steps:.1f}")
    print(f"  Success  (R)  : {success_rate:.1f}%")
    print(f"  Collision(C)  : {collision_rate:.1f}%")
    print(f"  Offroad  (O)  : {offroad_rate:.1f}%")
    print(f"  Too Far  (TF) : {toofar_rate:.1f}%")
    print(f"  Timeout  (T)  : {timeout_rate:.1f}%")
    print(f"{'='*40}")

    writer.add_scalar('BestModel/AvgReward',    avg_reward,     0)
    writer.add_scalar('BestModel/AvgSteps',     avg_steps,      0)
    writer.add_scalar('BestModel/SuccessRate',  success_rate,   0)
    writer.add_scalar('BestModel/CollisionRate',collision_rate, 0)
    writer.add_scalar('BestModel/OffroadRate',  offroad_rate,   0)

    actual_model.train()

if __name__ == '__main__':
    with open(INTESECTION_JSON, 'r') as f:
        junctions = json.load(f)
    env = CarlaEnv()
    test_tasks, test_towns = get_task_info(TEST_JSON)
    writer = SummaryWriter(log_dir=LOG_DIR)
    batch_test_and_clean(env, test_tasks, junctions, writer)