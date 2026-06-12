import heapq
import random
import torch
import os
from envs.carla_env import CarlaEnv
from hyperparameter import *
from constants import *
from utils.utils import *
from bc import *
from utils.carla_server import start_carla, stop_carla
import glob
import re
import os
import torch
import shutil

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
    # Sort by Episode number
    files.sort(key=lambda x: int(re.search(r'ep(\d+)', x).group(1)))
    return files

def batch_test_and_clean(env, test_tasks, junctions):
    ckpt_list = get_all_checkpoints()
    print(f"--- Found {len(ckpt_list)} models to test ---")

    records = load_latest_record(False)
    top_k = []  # (avg_reward, ckpt_path, ep_num)
    K = 25

    for ckpt_path in ckpt_list:
        ep_num = int(re.search(r'ep(\d+)', ckpt_path).group(1))
        print(f"\n>>> Testing Episode {ep_num} ...")
        
        try:
            models = load_checkpoint(ckpt_path, DEVICE)
        except Exception as e:
            print(f"Failed to load {ckpt_path}: {e}")
            continue

        total_test_reward = 0
        num_trials = 5
        for _ in range(num_trials):
            reward = test(env, TOWN, test_tasks, junctions, models['actor'], ep_num)
            total_test_reward += reward
        
        avg_reward = total_test_reward / num_trials
        print(f"Episode {ep_num} Average Reward: {avg_reward:.2f}")

        heapq.heappush(top_k, (avg_reward, ckpt_path, ep_num))
        if len(top_k) > K:
            heapq.heappop(top_k)  # Pop the minimum, keep top K

        records.append({'episode': ep_num, 'avg_reward': avg_reward})

    save_record(records, "test_raw")

    if not top_k:
        print("No models available")
        return

    # Sort from high to low
    top_k.sort(key=lambda x: x[0], reverse=True)
    print(f"\n--- Top {K} Models ---")
    
    all_summaries = []
    for rank, (avg_reward, ckpt_path, ep_num) in enumerate(top_k, 1):
        print(f"\n[{rank}] Episode {ep_num} | Avg Reward: {avg_reward:.2f}")
        print("--- Starting Detailed Evaluation ---")
        models = load_checkpoint(ckpt_path, DEVICE)
        summary = detailed_test(env, TOWN, test_tasks, junctions, models['actor'], ep_num, num_trials=50)
        summary['rank'] = rank
        all_summaries.append(summary)

    save_record(all_summaries, "test_summary")
    
def detailed_test(env, target_town, tasks, junctions, actor, ep_num, num_trials=50):
    actual_actor = actor._orig_mod if hasattr(actor, "_orig_mod") else actor
    actual_actor.eval()

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
                mu, _ = actual_actor(v_input, g_input)
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

    # Summary / Statistics
    reasons = results['reason']
    total = len(reasons)

    success_rate   = reasons.count('R')  / total * 100
    collision_rate = reasons.count('C')  / total * 100
    offroad_rate   = reasons.count('O')  / total * 100
    # toofar_rate    = reasons.count('TF') / total * 100
    timeout_rate   = reasons.count('T')  / total * 100

    avg_reward = sum(results['reward']) / total
    avg_steps  = sum(results['steps'])  / total

    print(f"\n{'='*40}")
    print(f"  Detailed Evaluation Results ({total} times)")
    print(f"{'='*40}")
    print(f"  Average Reward : {avg_reward:.2f}")
    print(f"  Average Steps  : {avg_steps:.1f}")
    print(f"  Success  (R)  : {success_rate:.1f}%")
    print(f"  Collision(C)  : {collision_rate:.1f}%")
    print(f"  Offroad  (O)  : {offroad_rate:.1f}%")
    print(f"  Timeout  (T)  : {timeout_rate:.1f}%")
    print(f"{'='*40}")

    summary = {
        'episode': ep_num,
        'avg_reward': avg_reward,
        'avg_steps': avg_steps,
        'success_rate': success_rate,
        'collision_rate': collision_rate,
        'offroad_rate': offroad_rate,
        'timeout_rate': timeout_rate,
    }
    return summary

if __name__ == '__main__':
    with open(INTESECTION_JSON, 'r') as f:
        junctions = json.load(f)
    start_carla()
    env = CarlaEnv(town=TOWN)
    test_tasks, test_towns = get_task_info(TEST_JSON)
    batch_test_and_clean(env, test_tasks, junctions)
    stop_carla()