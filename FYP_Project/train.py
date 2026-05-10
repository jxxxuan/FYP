import gc
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
from start_carla import restart_carla
from test import test

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

def update_networks(models, buffer):
    b_s, a, r, b_ns, d = buffer.sample(E_BATCH_SIZE, A_BATCH_SIZE)
    
    actor, critic = models['actor'], models['critic']
    actor_opt, critic_opt = models['actor_opt'], models['critic_opt']
    scaler = models['scaler']

    current_alpha = models['log_alpha'].exp().item()
    
    with torch.autocast(device_type="cuda"):
        with torch.no_grad():
            next_a, next_log_prob = actor.sample_action_with_logprob(b_ns['visual'], b_ns['goal'])
            t_q1, t_q2 = models['target_critic'](b_ns['visual'], b_ns['goal'], next_a)
            target_q = torch.min(t_q1, t_q2) - current_alpha * next_log_prob
            y = r + GAMMA * (1 - d) * target_q

        q1, q2 = critic(b_s['visual'], b_s['goal'], a)
        critic_loss = F.mse_loss(q1, y) + F.mse_loss(q2, y)

    actor_loss = torch.tensor(0.0, device=DEVICE)
    alpha_loss = torch.tensor(0.0, device=DEVICE)

    critic_opt.zero_grad()
    scaler.scale(critic_loss).backward()
    scaler.step(critic_opt)
    
    for p in critic.parameters(): p.requires_grad = False
    with torch.autocast(device_type="cuda"):
        new_a, log_prob = actor.sample_action_with_logprob(b_s['visual'], b_s['goal'])
        current_q1, current_q2 = critic(b_s['visual'], b_s['goal'], new_a)
        actor_loss = (current_alpha * log_prob - torch.min(current_q1, current_q2)).mean()

    alpha_loss = -(models['log_alpha'] * (log_prob + models['target_entropy']).detach()).mean()
    models['alpha_opt'].zero_grad()
    alpha_loss.backward()
    models['alpha_opt'].step()

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
            
def train(env, town, task, junctions, models, buffer, episode, writer):
    junction_name = task['junction_name']
    junction_data = junctions[town].get('train_junctions', {}).get(junction_name, [])

    start, target = build_pose(task)
    obs, _ = env.reset(town, level=0.2, junction_data=junction_data, start_transform=start, target_location=target)
    # initial_frames = env.obs_buffer.visual_pool # (4, H, W, 3)
    # initial_goals = env.obs_buffer.goal_pool
    # for i in range(4):
    #     temp_state = {
    #         'visual': initial_frames[:i+1], 
    #         'goal': initial_goals[i]
    #     }
    #     buffer.add_agent_experience(temp_state, np.zeros(2), 0.0, False)

    losses = {'critic': 0, 'actor': 0, 'alpha': 0, 'alpha_loss': 0}
    
    total_reward = 0
    t1 = time.time()

    for step in range(MAX_STEPS):
        v_in, g_in = preprocess_obs(obs['visual'], obs['goal'], DEVICE)
        with torch.no_grad():
            a_tensor, _ = models['actor'].sample_action_with_logprob(v_in, g_in)
        a_np = a_tensor.cpu().numpy()[0]
        
        next_obs, r, term, trunc, info = env.step(a_np)
        buffer.add_agent_experience(obs, a_tensor, r, term)

        if step % UPDATE_PER_STEP == 0 and len(buffer.agent_valid_indices) > A_BATCH_SIZE:
            losses = update_networks(models, buffer)
            writer.add_scalar(f'Loss/Critic', losses['critic'], models['global_step'])
            writer.add_scalar(f'Loss/Actor', losses['actor'], models['global_step'])
            writer.add_scalar(f'Alpha/loss', losses['alpha_loss'], models['global_step'])
            writer.add_scalar(f'Alpha/Value', losses['alpha'], models['global_step'])
            models['global_step'] += 1

        obs = next_obs
        total_reward += r
        if term or trunc: break

    print(f"[{episode}] {town} Reward: {total_reward:.2f} | Time: {time.time()-t1:.1f}s | Reason: {info['reason']}")
    writer.add_scalar('Reward/Train', total_reward, episode)
    return losses

def soft_update(net, target_net, tau):
    """
    将 net 的参数缓慢融合到 target_net 中
    """
    for param, target_param in zip(net.parameters(), target_net.parameters()):
        # target = tau * current + (1 - tau) * target
        target_param.data.copy_(
            tau * param.data + (1.0 - tau) * target_param.data
        )

if __name__ == '__main__':
    # restart_carla_docker()
    env = CarlaEnv()
    target_entropy = -float(ACTION_DIM) 

    log_alpha = torch.zeros(1, requires_grad=True, device=DEVICE)
    alpha_opt = torch.optim.Adam([log_alpha], lr=LR)

    scaler = torch.amp.GradScaler('cuda')

    start_episode, models = load_latest_checkpoint(DEVICE)
    start_updates = models['global_step']
    models['target_entropy'] = target_entropy
    models['scaler'] = scaler

    buffer = MixedReplayBuffer(DEVICE, agent_capacity=AGENT_BUFFER_SIZE)
    buffer.load_expert_data()
    buffer.load_agent_buffer()

    writer = SummaryWriter(log_dir=LOG_DIR)

    if start_episode == 0:
        print("--- Loading Expert Data for BC Pre-training ---")
        behavioral_cloning_pretrain(models['actor'], models['actor_opt'], writer, buffer, iterations=BC_ITER)

    gc.collect()
    torch.cuda.empty_cache()

    if hasattr(torch, 'compile'):
        print("--- Compiling models for speedup... ---")
        actor = torch.compile(models['actor'], mode="reduce-overhead")
        critic = torch.compile(models['critic'], mode="reduce-overhead")

    actual_critic = critic._orig_mod if hasattr(critic, "_orig_mod") else critic
    models['target_critic'].load_state_dict(actual_critic.state_dict())
    for param in models['target_critic'].parameters():
        param.requires_grad = False

    total_updates = start_updates
    
    with open(INTESECTION_JSON, 'r') as f:
        junctions = json.load(f)
    
    train_tasks, train_towns = get_task_info(TRAIN_JSON)
    test_tasks, test_towns = get_task_info(TEST_JSON)
    train_stream = get_task_stream(train_tasks, train_towns,"Town04")

    town_pointers = {town: 0 for town in train_towns}
    current_town_idx = 0

    try:
        for current_episode in range(start_episode, MAX_EPISODES):
            current_town, current_task = next(train_stream)
            junction_name = current_task.get('junction_name', 'Unknown')
            print(f"--- Ep {current_episode} | Town: {current_town} | Junction: {junction_name} ---")
            losses = train(env, current_town, current_task, junctions, models, buffer, current_episode, writer)

            if current_episode % CHECK_POINT_INTERVAL == 0:
                save_checkpoint(actor, models['actor_opt'], critic, models['critic_opt'], alpha_opt, log_alpha, current_episode, models['global_step'])
                
                buffer.save_agent_buffer(current_episode)
                # test(env, target_town="Town04", tasks=test_tasks, junctions=junctions, actor=actor, current_episode=current_episode, writer=writer)
                # env.close()
                # restart_carla_docker()
                # for i in range(5):
                #     try:
                #         env = CarlaEnv()
                #         break
                #     except Exception as e:
                #         print(f"CarlaEnv init failed ({i+1}/5): {e}")
                #         time.sleep(5)
                # else:
                #     raise RuntimeError("Cannot reconnect to CARLA")

    except KeyboardInterrupt:
        print("\n[DETECTED] Ctrl+C")
    except Exception as e:
        print(f"\n[ERROR] : {e}")
        raise e
    finally:
        # send_mail("Stop running","Please check")
        save_checkpoint(actor, models['actor_opt'], critic, models['critic_opt'], alpha_opt, log_alpha, current_episode, models['global_step'])
        writer.close()
        env.close()