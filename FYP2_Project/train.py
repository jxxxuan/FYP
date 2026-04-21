import random
import torch
from envs.carla_env import CarlaEnv
from models.sac_agent import MixedReplayBuffer
import torch.nn.functional as F
from torch.utils.tensorboard import SummaryWriter
import os
from hyperparameter import *
from constants import *
import json
from utils.utils import *
from bc import *

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def train(env, scenarios, actor, actor_opt, critic, critic_opt, target_critic, buffer, start_episode, start_updates):
    writer = SummaryWriter(log_dir=LOG_DIR)

    if start_episode == 0:
        print("--- Loading Expert Data for BC Pre-training ---")
        behavioral_cloning_pretrain(actor, actor_opt, writer, buffer, device, iterations=1000)
        torch.cuda.empty_cache()

    if hasattr(torch, 'compile'):
        print("--- Compiling models for speedup... ---")
        actor = torch.compile(actor, mode="reduce-overhead")
        critic = torch.compile(critic, mode="reduce-overhead")

    # 实例化 Actor 和 Double Critic
    actual_critic = critic._orig_mod if hasattr(critic, "_orig_mod") else critic
    
    target_critic.load_state_dict(actual_critic.state_dict())
    # target_critic.load_state_dict(critic.state_dict())
    for param in target_critic.parameters():
        param.requires_grad = False
    
    target_entropy = -float(action_dim) 

    # 初始化 log_alpha 为 0 (即 alpha=1)
    log_alpha = torch.zeros(1, requires_grad=True, device=device)
    alpha_opt = torch.optim.Adam([log_alpha], lr=LR)

    # 当前时刻的 alpha 值
    alpha = log_alpha.exp().item()

    scaler = torch.amp.GradScaler('cuda')

    total_updates = start_updates
    
    available_towns = list(scenarios.keys())
    # available_towns = ['Town04']

    town_task_lists = {}
    for town in available_towns:
        tasks_in_this_town = []
        for junction_name in sorted(scenarios[town].keys()):
            junction_data = scenarios[town][junction_name]
            if isinstance(junction_data, dict) and 'tasks' in junction_data:
                for t in junction_data['tasks']:
                    if t.get('valid') == True:
                        # 将 junction_name 注入到 task 对象中，方便后续找文件夹
                        t['junction_name'] = junction_name 
                        tasks_in_this_town.append(t)
        town_task_lists[town] = tasks_in_this_town

    town_pointers = {town: 0 for town in available_towns}
    current_town_idx = 0
    current_town = available_towns[current_town_idx]
    all_tasks = town_task_lists[current_town]

    # 2. 初始化各 Town 的当前任务指针
    try:
        # 3. 主训练循环
        for current_episode in range(start_episode, 4000):  # 论文实验进行了2000个回次
            if town_pointers[current_town] >= len(all_tasks):
                town_pointers[current_town] = 0 # 重置旧地图指针
                current_town_idx = (current_town_idx + 1) % len(available_towns) # 切换索引
                current_town = available_towns[current_town_idx] # 更新地图名
                all_tasks = town_task_lists[current_town] # 更新任务列表
                torch.cuda.empty_cache()
                print(f"\n>>>>>>> Switch to {current_town} <<<<<<<")

            # fixed_task_index = 0
            # task = all_tasks[fixed_task_index]
            task = all_tasks[town_pointers[current_town]]
            town_pointers[current_town] += 1

            should_test = (current_episode % CHECK_POINT_INTERVAL == 0)

            print(f"[{current_episode}] scenario: {current_town} | junction index: {task['task_id']}/{len(all_tasks)}")

            start, target = build_pose(task)
            obs, _ = env.reset(current_town, level=0, start_transform=start, target_location=target)
            
            episode_reward = 0

            t1 = time.time()
            for step in range(MAX_STEPS):  # 每回次最大步数
                v_input, g_input = preprocess_obs(obs['visual'], obs['goal'], device)

                # 2. 选择动作
                action_tensor, _ = actor.sample_action_with_logprob(v_input, g_input)
                action_numpy = action_tensor.detach().cpu().numpy()[0]
                
                # 3. 环境交互
                next_obs, reward, terminated, truncated, _ = env.step(action_numpy)
                
                # 保存到智能体缓冲区
                buffer.add_agent_experience(obs, action_numpy, reward, terminated)
                
                # 开始更新网络 (如果缓冲区数据足够)
                if step % UPDATE_PER_STEP == 0 and buffer.agent_size > A_BATCH_SIZE:
                    # 混合采样：128个智能体样本 + 128个专家样本
                    b_s, a, r, b_ns, d = buffer.sample(E_BATCH_SIZE, A_BATCH_SIZE)
                    s_v, s_g = b_s['visual'], b_s['goal']
                    ns_v, ns_g = b_ns['visual'], b_ns['goal']
                    
                    with torch.no_grad():
                        with torch.autocast(device_type="cuda"):
                            # 获取下一状态的动作和 log_prob
                            next_action, next_log_prob = actor.sample_action_with_logprob(ns_v, ns_g)
                            # 使用 Target Critic 计算目标
                            target_q1, target_q2 = target_critic(ns_v, ns_g, next_action)
                            target_q = torch.min(target_q1, target_q2) - alpha * next_log_prob
                            # 计算 y (Reward + Gamma * Target_Q)
                            y = r + GAMMA * (1 - d) * target_q

                    # Critic 更新
                    with torch.autocast(device_type="cuda"):
                        curr_q1, curr_q2 = critic(s_v, s_g, a)
                        critic_loss = F.mse_loss(curr_q1, y) + F.mse_loss(curr_q2, y)
                    critic_opt.zero_grad()
                    scaler.scale(critic_loss).backward()
                    scaler.step(critic_opt)
                    scaler.update()

                    # Actor 更新
                    for p in critic.parameters(): p.requires_grad = False

                    with torch.autocast(device_type="cuda"):
                        new_action, log_prob = actor.sample_action_with_logprob(s_v, s_g)
                        q1, q2 = critic(s_v, s_g, new_action)
                        actor_loss = (alpha * log_prob - torch.min(q1, q2)).mean()
                    actor_opt.zero_grad()
                    scaler.scale(actor_loss).backward()
                    scaler.step(actor_opt)

                    for p in critic.parameters(): p.requires_grad = True

                    scaler.update()
                    
                    # --- 软更新目标网络 ---
                    for param, target_param in zip(critic.parameters(), target_critic.parameters()):
                        target_param.data.copy_(TAU * param.data + (1 - TAU) * target_param.data)

                    alpha_loss = -(log_alpha * (log_prob + target_entropy).detach()).mean()

                    # 2. 梯度下降更新 log_alpha
                    alpha_opt.zero_grad()
                    alpha_loss.backward()
                    alpha_opt.step()

                    # 3. 更新当前使用的 alpha 变量
                    alpha = log_alpha.exp().item()

                    total_updates += 1
                    writer.add_scalar('Alpha/Value', alpha, total_updates)
                    writer.add_scalar('Alpha/Loss', alpha_loss.item(), total_updates)
                    writer.add_scalar('Loss/Critic', critic_loss.item(), total_updates)
                    writer.add_scalar('Loss/Actor', actor_loss.item(), total_updates)
                
                obs = next_obs
                episode_reward += reward
                if terminated or truncated:
                    break

            print(f"Train Reward: {episode_reward} | Time consumed: {time.time()-t1}s")
            writer.add_scalar('Reward/Train', episode_reward, current_episode)

            if should_test:
                test_task = random.choice(all_tasks)
                save_checkpoint(actor, actor_opt, critic, critic_opt, current_episode, total_updates)
                test(env, actor, current_town, test_task, current_episode, writer)
                
    except KeyboardInterrupt:
        print("\n[DETECTED] Ctrl+C")
    except Exception as e:
        print(f"\n[ERROR] : {e}")
        raise e # 重新抛出异常以便调试
    finally:
        save_checkpoint(actor, actor_opt, critic, critic_opt, current_episode, total_updates)
        writer.close()
        print("Saved")
        env.close()

@torch.no_grad()
def test(env, actor, current_town, task, current_episode, writer):
    """
    针对特定任务进行测试
    """
    # 切换到评估模式 (关闭 Dropout 等)
    actual_actor = actor._orig_mod if hasattr(actor, "_orig_mod") else actor
    actual_actor.eval()
    
    test_rewards = []
    
    video_path = os.path.join(CP_DIR, f"debug_{current_town}_ep{current_episode}.mp4")
    start, target = build_pose(task)

    obs, _ = env.reset(current_town, level=0, start_transform=start, target_location=target, video_path=video_path)
    
    episode_reward = 0
    done = False
    step = 0
    
    while step < MAX_STEPS and not done:
        # 1. 预处理 (与训练完全一致)
        v_input, g_input = preprocess_obs(obs['visual'], obs['goal'], device)

        # 2. 确定性动作：直接取 mu (不采样，不加噪声)
        # 你需要确保你的 Actor.forward 返回的是 (mu, sigma)
        mu, _ = actual_actor(v_input, g_input)
        action = torch.tanh(mu) # SAC 的动作通常通过 tanh 映射到 [-1, 1]
        action_numpy = action.detach().cpu().numpy()[0]
        
        # 3. 执行动作
        next_obs, reward, terminated, truncated, _ = env.step(action_numpy)
        
        obs = next_obs
        episode_reward += reward
        step += 1
        done = terminated or truncated
            
    print(f"Test Run Reward: {episode_reward:.2f} | Steps: {step}")
    writer.add_scalar('Reward/Test', episode_reward, current_episode)
    test_rewards.append(episode_reward)

    # 切回训练模式
    actual_actor.train()

if __name__ == '__main__':
    with open(os.path.join(DRIVE_PATH, 'train_tasks.json'), 'r') as f:
        scenarios = json.load(f)

    # 初始化环境与模型
    env = CarlaEnv(npc=True)
    action_dim = env.action_space.shape[0]

    # 1. Actor 的视觉编码器
    actor, critic, target_critic, actor_opt, critic_opt = create_model(action_dim, device)

    start_episode, start_updates = load_latest_checkpoint(actor, actor_opt, critic, critic_opt, target_critic, device)

    buffer = MixedReplayBuffer(device, agent_capacity=100000)
    buffer.load_expert_data(ED_DIR) # 确保 ED_DIR 路径正确
    buffer.split_expert_data(val_ratio=0.1)

    train(env, scenarios, actor, actor_opt, critic, critic_opt, target_critic, buffer, start_episode, start_updates)