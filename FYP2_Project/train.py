import random
import torch
from envs.carla_env import CarlaEnv
from models.sac_agent import MixedReplayBuffer
import torch.nn.functional as F
from torch.utils.tensorboard import SummaryWriter
import os
from hyperparameter import *
from constants import *
from utils.utils import *
from bc import *

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def update_networks(models, buffer, update_actor):
    # 1. 混合采样
    b_s, a, r, b_ns, d = buffer.sample(E_BATCH_SIZE, A_BATCH_SIZE)
    
    # 提取模型和优化器
    actor, critic = models['actor'], models['critic']
    actor_opt, critic_opt = models['actor_opt'], models['critic_opt']
    scaler = models['scaler']

    current_alpha = models['log_alpha'].exp().item()
    
    # --- SAC 核心数学逻辑 ---
    with torch.autocast(device_type="cuda"):
        # 计算 Target Q (目标值)
        with torch.no_grad():
            next_a, next_log_prob = actor.sample_action_with_logprob(b_ns['visual'], b_ns['goal'])
            t_q1, t_q2 = models['target_critic'](b_ns['visual'], b_ns['goal'], next_a)
            target_q = torch.min(t_q1, t_q2) - current_alpha * next_log_prob
            y = r + GAMMA * (1 - d) * target_q

        q1, q2 = critic(b_s['visual'], b_s['goal'], a)
        critic_loss = F.mse_loss(q1, y) + F.mse_loss(q2, y)

    actor_loss = torch.tensor(0.0, device=device)
    alpha_loss = torch.tensor(0.0, device=device)

    critic_opt.zero_grad()
    scaler.scale(critic_loss).backward()
    scaler.step(critic_opt)
    
    # 更新 Actor (冻结 Critic 梯度以节省计算)
    if update_actor:
        for p in critic.parameters(): p.requires_grad = False
        with torch.autocast(device_type="cuda"):
            new_a, log_prob = actor.sample_action_with_logprob(b_s['visual'], b_s['goal'])
            current_q1, current_q2 = critic(b_s['visual'], b_s['goal'], new_a)
            actor_loss = (current_alpha * log_prob - torch.min(current_q1, current_q2)).mean()

        alpha_loss = -(models['log_alpha'] * (log_prob + models['target_entropy']).detach()).mean()
        models['alpha_opt'].zero_grad()
        alpha_loss.backward()
        models['alpha_opt'].step()

        # 执行 Actor 的反向传播和梯度更新
        actor_opt.zero_grad()
        scaler.scale(actor_loss).backward()
        scaler.step(actor_opt)

    for p in critic.parameters(): p.requires_grad = True

    scaler.update()
    soft_update(critic, models['target_critic'], TAU)

    return {
        'critic': critic_loss.item(),
        'actor': actor_loss.item(),
        'alpha': current_alpha,
        'alpha_loss': alpha_loss.item()
    }
            
def train(env, town, task, scenarios, models, buffer, episode, writer):
    junction_name = task['junction_name']
    # 简化：使用 dict.get 的链式调用
    j_data = scenarios[town][junction_name].get('test_junctions', {}).get(town, [])

    start, target = build_pose(task)
    obs, _ = env.reset(town, level=0.2, junction_data=j_data, start_transform=start, target_location=target)
    
    total_reward = 0
    t1 = time.time()

    for step in range(MAX_STEPS):
        # 1. 交互
        v_in, g_in = preprocess_obs(obs['visual'], obs['goal'], device)
        with torch.no_grad():
            a_tensor, _ = models['actor'].sample_action_with_logprob(v_in, g_in)
        a_np = a_tensor.cpu().numpy()[0]
        
        next_obs, r, term, trunc, _ = env.step(a_np)
        buffer.add_agent_experience(obs, a_np, r, term)

        # 2. 极简更新逻辑 (假设更新函数被封装)
        if step % UPDATE_PER_STEP == 0 and buffer.agent_size > A_BATCH_SIZE:
            update_actor = (episode >= 100)
            losses = update_networks(models, buffer, update_actor) # 将复杂的 SAC 公式封装
            for k, v in losses.items():
                writer.add_scalar(f'Loss/{k}', v, models['global_step'])
            models['global_step'] += 1

        obs = next_obs
        total_reward += r
        if term or trunc: break

    print(f"[{episode}] {town} Reward: {total_reward:.2f} | Time: {time.time()-t1:.1f}s")
    writer.add_scalar('Reward/Train', total_reward, episode)

def soft_update(net, target_net, tau):
    """
    将 net 的参数缓慢融合到 target_net 中
    """
    for param, target_param in zip(net.parameters(), target_net.parameters()):
        # 计算公式: target = tau * current + (1 - tau) * target
        target_param.data.copy_(
            tau * param.data + (1.0 - tau) * target_param.data
        )

@torch.no_grad()
def test(env, actor, current_episode, writer, scenarios, town_task_lists, target_town="Town03"):
    """
    针对特定任务进行测试
    """
    tasks_in_town = town_task_lists.get(target_town, [])
    if not tasks_in_town:
        return
    
    selected_task = random.choice(tasks_in_town)
    junction_name = selected_task['junction_name']
    junction_data = scenarios[target_town][junction_name].get('test_junctions', {}).get(target_town, [])
    
    # 切换到评估模式 (关闭 Dropout 等)
    actual_actor = actor._orig_mod if hasattr(actor, "_orig_mod") else actor
    actual_actor.eval()
    
    video_path = os.path.join(CP_DIR, f"debug_{target_town}_ep{current_episode}.mp4")
    start, target = build_pose(selected_task)

    obs, _ = env.reset(target_town, level=0, junction_data=junction_data, start_transform=start, target_location=target, video_path=video_path)
    
    episode_reward = 0
    done = False
    step = 0
    
    while step < MAX_STEPS + (MAX_STEPS * 0.2) and not done:
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

    # 切回训练模式
    actual_actor.train()

if __name__ == '__main__':

    # 初始化环境与模型
    env = CarlaEnv(npc=True)
    action_dim = env.action_space.shape[0]

    # 1. Actor 的视觉编码器
    actor, critic, target_critic, actor_opt, critic_opt = create_model(action_dim, device)

    target_entropy = -float(action_dim) 

    # 初始化 log_alpha 为 0 (即 alpha=1)
    log_alpha = torch.zeros(1, requires_grad=True, device=device)
    alpha_opt = torch.optim.Adam([log_alpha], lr=LR)
    alpha = log_alpha.exp().item()

    scaler = torch.amp.GradScaler('cuda')

    start_episode, start_updates = load_latest_checkpoint(actor, actor_opt, critic, critic_opt, target_critic, device)

    models = {
        'actor': actor, 'actor_opt': actor_opt,
        'critic': critic, 'critic_opt': critic_opt,
        'target_critic': target_critic,
        'log_alpha': log_alpha, 'alpha_opt': alpha_opt,
        'target_entropy': target_entropy,
        'scaler': scaler, 'global_step': start_updates
    }

    buffer = MixedReplayBuffer(device, agent_capacity=100000)
    buffer.load_expert_data(ED_DIR) # 确保 ED_DIR 路径正确
    buffer.split_expert_data(val_ratio=0.1)

    writer = SummaryWriter(log_dir=LOG_DIR)

    if start_episode == 0:
        print("--- Loading Expert Data for BC Pre-training ---")
        behavioral_cloning_pretrain(actor, actor_opt, writer, buffer, device, iterations=1500)
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

    total_updates = start_updates
    
    train_scenarios, train_tasks, train_towns = get_task_info(TRAIN_JSON)
    test_scenarios, test_tasks, test_towns = get_task_info(TEST_JSON)
    train_stream = get_task_stream(train_tasks, train_towns)

    town_pointers = {town: 0 for town in train_towns}
    current_town_idx = 0

    try:
        for current_episode in range(start_episode, 5000):
            current_town, current_task = next(train_stream)
            train(env, current_town, current_task, train_scenarios, models, buffer, current_episode, writer)

            if current_episode % CHECK_POINT_INTERVAL == 0:
                save_checkpoint(actor, actor_opt, critic, critic_opt, current_episode, models['global_step'])
                test(env, actor, current_episode, writer, test_scenarios, test_tasks, target_town="Town03")

    except KeyboardInterrupt:
        print("\n[DETECTED] Ctrl+C")
    except Exception as e:
        print(f"\n[ERROR] : {e}")
        raise e # 重新抛出异常以便调试
    finally:
        save_checkpoint(actor, actor_opt, critic, critic_opt, current_episode, models['global_step'])
        writer.close()
        print("Saved")
        env.close()