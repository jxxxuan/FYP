import torch
import torch.optim as optim
from envs.carla_env import CarlaEnv
from models.sac_agent import Actor, DoubleCritic, MixedReplayBuffer
import torch.nn.functional as F
from torch.utils.tensorboard import SummaryWriter
import os
from hyperparameter import *
from constants import *
import json
import carla
from utils.utils import *

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"--- Device: {device} ({torch.cuda.get_device_name(0)}) ---")

def train(env, scenarios, actor, actor_opt, critic, critic_opt, target_critic, expert_data_dir, start_episode, start_updates):
    # 实例化 Actor 和 Double Critic
    writer = SummaryWriter(log_dir=LOG_DIR)
    
    actual_critic = critic._orig_mod if hasattr(critic, "_orig_mod") else critic
    
    target_critic.load_state_dict(actual_critic.state_dict())
    # target_critic.load_state_dict(critic.state_dict())
    for param in target_critic.parameters():
        param.requires_grad = False
    
    # 2. 初始化混合缓冲区
    buffer = MixedReplayBuffer(device, agent_capacity=20000)

    scaler = torch.amp.GradScaler('cuda')

    total_updates = start_updates
    
    available_towns = list(scenarios.keys())

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
    loaded_junction_key = None

    # 2. 初始化各 Town 的当前任务指针
    try:
        current_town = available_towns[current_town_idx]
        all_tasks = town_task_lists[current_town]
        # 3. 主训练循环
        for current_episode in range(start_episode, 2000):  # 论文实验进行了2000个回次
            if town_pointers[current_town] >= len(all_tasks):
                town_pointers[current_town] = 0 # 重置旧地图指针
                current_town_idx = (current_town_idx + 1) % len(available_towns) # 切换索引
                current_town = available_towns[current_town_idx] # 更新地图名
                all_tasks = town_task_lists[current_town] # 更新任务列表
                print(f"\n>>>>>>> Switch to {current_town} <<<<<<<")

            task = all_tasks[town_pointers[current_town]]
            town_pointers[current_town] += 1

            current_junction = task['junction_name']
            junction_key = f"{current_town}/{current_junction}"

            if junction_key != loaded_junction_key:
                specific_expert_dir = os.path.join(expert_data_dir, current_town, current_junction)
                print(specific_expert_dir)
                print(f"\n--- [Switching Junction] {junction_key} ---")
                buffer.clear_expert_data() 
                buffer.load_expert_data(specific_expert_dir)
                loaded_junction_key = junction_key
                torch.cuda.empty_cache() # 清理显存

            should_record = (current_episode % CHECK_POINT_INTERVAL == 0)
            video_file = os.path.join(CP_DIR, f"debug_{current_town}_ep{current_episode}.mp4") if should_record else None

            print(f"[{current_episode}] scenario: {current_town} | junction index: {task['task_id']}/{len(all_tasks)}")

            s = task['start_pose']
            t = task['target_pose']
            start_transform = carla.Transform(
                    carla.Location(x=s['x'], y=s['y'], z=s['z']), # 抬高防卡地
                    carla.Rotation(yaw=s['rotate'])
                )
            target_loc = carla.Location(x=t['x'], y=t['y'], z=t['z'])
            obs, _ = env.reset(current_town, video_path = video_file, start_transform=start_transform, target_location=target_loc)
            episode_reward = 0

            t1 = time.time()
            for step in range(500):  # 每回次最大步数
                # 选择动作
                action_tensor,_ = actor.sample_action_with_logprob(
                    torch.FloatTensor(obs['visual']).cuda().permute(0, 1, 4, 2, 3).reshape(1, 12, 96, 256),
                    torch.FloatTensor(obs['goal']).cuda()
                )
                action_numpy = action_tensor.detach().cpu().numpy()[0]
                # 环境交互
                next_obs, reward, terminated, truncated, info = env.step(action_numpy)
                
                # 保存到智能体缓冲区
                buffer.add_agent_experience(obs, action_numpy, reward, next_obs, terminated)
                
                # 开始更新网络 (如果缓冲区数据足够)
                if step % UPDATE_PER_STEP == 0 and len(buffer.agent_buffer) > 500:
                    for _ in range(2):
                        # 混合采样：128个智能体样本 + 128个专家样本
                        b_s, a, r, b_ns, d = buffer.sample(BATCH_SIZE)
                        s_v, s_g = b_s['visual'], b_s['goal']
                        ns_v, ns_g = b_ns['visual'], b_ns['goal']
                        
                        with torch.no_grad():
                            with torch.autocast(device_type="cuda"):
                                # 获取下一状态的动作和 log_prob
                                next_action, next_log_prob = actor.sample_action_with_logprob(ns_v, ns_g)
                                # 使用 Target Critic 计算目标
                                target_q1, target_q2 = target_critic(ns_v, ns_g, next_action)
                                target_q = torch.min(target_q1, target_q2) - ALPHA * next_log_prob
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
                            actor_loss = (ALPHA * log_prob - torch.min(q1, q2)).mean()
                        actor_opt.zero_grad()
                        scaler.scale(actor_loss).backward()
                        scaler.step(actor_opt)

                        for p in critic.parameters(): p.requires_grad = True

                        scaler.update()
                        
                        # --- 软更新目标网络 ---
                        for param, target_param in zip(critic.parameters(), target_critic.parameters()):
                            target_param.data.copy_(TAU * param.data + (1 - TAU) * target_param.data)

                        total_updates += 1
                        writer.add_scalar('Loss/Critic', critic_loss.item(), total_updates)
                        writer.add_scalar('Loss/Actor', actor_loss.item(), total_updates)
                
                obs = next_obs
                episode_reward += reward
                if terminated or truncated:
                    break

            writer.add_scalar('Reward/Episode', episode_reward, current_episode)
            print(f"reward: {episode_reward} | Time consumed: {time.time()-t1}s")
            if should_record:
                save_checkpoint(actor, actor_opt, critic, critic_opt, current_episode, total_updates)
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

if __name__ == '__main__':
    with open(os.path.join(DRIVE_PATH, 'train_tasks.json'), 'r') as f:
        scenarios = json.load(f)

    # 1. Actor 的视觉编码器
    vit_encoder_a = create_vit()

    # 2. Critic 的视觉编码器 (用于 Double Q)
    # 论文中 Critic 网络共享相同的 ViT 架构 
    shared_vit_c = create_vit()

    # 3. Target Critic 的视觉编码器 (用于稳定训练) [cite: 227]
    shared_vit_tc = create_vit()

    # 初始化环境与模型
    env = CarlaEnv(npc=False)
    action_dim = env.action_space.shape[0]

    actor = Actor(vit_encoder_a, action_dim).to(device)
    critic = DoubleCritic(shared_vit_c, shared_vit_c, action_dim).to(device)
    target_critic = DoubleCritic(shared_vit_tc, shared_vit_tc, action_dim).to(device)

    actor_opt = optim.Adam(actor.parameters(), lr=LR)
    critic_opt = optim.Adam(critic.parameters(), lr=LR)

    start_episode, start_updates = load_latest_checkpoint(actor, actor_opt, critic, critic_opt, target_critic, device)

    if hasattr(torch, 'compile'):
        print("--- Compiling models for speedup... ---")
        actor = torch.compile(actor, mode="reduce-overhead")
        critic = torch.compile(critic, mode="reduce-overhead")

    train(env, scenarios, actor, actor_opt, critic, critic_opt, target_critic, ED_N_DIR, start_episode, start_updates)