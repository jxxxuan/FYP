import gc
import pandas as pd
import torch
from torch.distributions import Normal
from envs.carla_env import CarlaEnv
from models.sac_agent import MixedReplayBuffer
import torch.nn.functional as F
import os
from hyperparameter import *
from constants import *
from utils.utils import *
from bc import *
from torch.utils.tensorboard import SummaryWriter
from start_carla import restart_carla
from test import test

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

def update_networks(models, buffer, update_a=True):
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

    critic_opt.zero_grad()
    scaler.scale(critic_loss).backward()
    scaler.step(critic_opt)

    actor_loss = torch.tensor(0.0, device=DEVICE)
    alpha_loss = torch.tensor(0.0, device=DEVICE)

    if update_a:
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
    }
            
def train(env, town, task, junctions, models, buffer, episode, writer):
    junction_name = task['junction_name']
    junction_data = junctions[town].get('train_junctions', {}).get(junction_name, [])

    start, target = build_pose(task)
    obs, _ = env.reset(town, level=0.2, junction_data=junction_data, start_transform=start, target_location=target)

    losses = {'critic': 0, 'actor': 0, 'alpha': 0, 'alpha_loss': 0}
    
    total_reward = 0
    t1 = time.time()

    for step in range(MAX_STEPS):
        v_in, g_in = preprocess_obs(obs['visual'], obs['goal'], DEVICE)
        with torch.no_grad():
            a_tensor, _ = models['actor'].sample_action_with_logprob(v_in, g_in)

        # with torch.no_grad():
        #     feat = models['model'].get_feature(v_in)
        #     mu, sigma = models['model'].actor(feat, g_in)
        #     dist = Normal(mu, sigma)
        #     z = dist.rsample()
        #     a_tensor = torch.tanh(z)
        a_np = a_tensor.cpu().numpy()[0]
        
        next_obs, r, term, trunc, info = env.step(a_np)
        buffer.add_agent_experience(obs, a_tensor, r, term)

        if step % UPDATE_PER_STEP == 0 and len(buffer._valid_set) > A_BATCH_SIZE:
            should_update_actor = (models['global_step'] % 2 == 0)
            losses = update_networks(models, buffer,update_a=should_update_actor)
            if should_update_actor:
                writer.add_scalar(f'Loss/Actor', losses['actor'], models['global_step'])
                writer.add_scalar(f'Alpha/Value', losses['alpha'], models['global_step'])
            writer.add_scalar(f'Loss/Critic', losses['critic'], models['global_step'])
            models['global_step'] += 1

        obs = next_obs
        total_reward += r
        if term or trunc: break

    print(f"[{episode}] {town} Reward: {total_reward:.2f} | Time: {time.time()-t1:.1f}s | Reason: {info['reason']} | Avr Speed: {info['average speed']}")
    writer.add_scalar('Reward/Train', total_reward, episode)
    return {
        'episode': episode,
        'reward': total_reward,
        'reason': info['reason'],
        'steps': step + 1,
        'time': round(time.time() - t1, 1),
        'critic_loss': losses['critic'],
        'actor_loss': losses['actor'],
        'alpha': losses['alpha'],
    }

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

    scaler = torch.amp.GradScaler('cuda')

    models = load_latest_checkpoint(DEVICE)
    records = load_latest_record()
    start_updates = models['global_step']
    models['target_entropy'] = target_entropy
    models['scaler'] = scaler

    buffer = MixedReplayBuffer(DEVICE, agent_capacity=AGENT_BUFFER_SIZE)
    buffer.load_expert_data()
    buffer.load_agent_buffer()

    writer = SummaryWriter(log_dir=LOG_DIR)

    if models['episode'] == 0:
        print("--- Loading Expert Data for BC Pre-training ---")
        behavioral_cloning_pretrain(models['actor'], models['actor_opt'], buffer, iterations=BC_ITER)
        # behavioral_cloning_pretrain(models['model'], models['opt'], buffer, iterations=BC_ITER)

    gc.collect()
    torch.cuda.empty_cache()

    if hasattr(torch, 'compile'):
        print("--- Compiling models for speedup... ---")
        models['actor'] = torch.compile(models['actor'], mode="reduce-overhead")
        models['critic'] = torch.compile(models['critic'], mode="reduce-overhead")

    actual_critic = models['critic']._orig_mod if hasattr(models['critic'], "_orig_mod") else models['critic']
    models['target_critic'].load_state_dict(actual_critic.state_dict())
    for param in models['target_critic'].parameters():
        param.requires_grad = False

    # actual_model = models['model']._orig_mod if hasattr(models['model'], "_orig_mod") else models['model']
    # models['target_model'].load_state_dict(actual_model.state_dict())
    # for param in models['target_model'].parameters():
    #     param.requires_grad = False

    total_updates = start_updates
    
    with open(INTESECTION_JSON, 'r') as f:
        junctions = json.load(f)
    
    train_tasks, train_towns = get_task_info(TRAIN_JSON)
    test_tasks, test_towns = get_task_info(TEST_JSON)
    train_stream = get_task_stream(train_tasks, train_towns,"Town04")

    town_pointers = {town: 0 for town in train_towns}
    current_town_idx = 0

    try:
        for current_episode in range(models['episode'], MAX_EPISODES):
            current_town, current_task = next(train_stream)
            junction_name = current_task.get('junction_name', 'Unknown')
            print(f"--- Ep {current_episode} | Town: {current_town} | Junction: {junction_name} ---")
            record = train(env, current_town, current_task, junctions, models, buffer, current_episode, writer)
            records.append(record)

            if current_episode % CHECK_POINT_INTERVAL == 0 and current_episode > 0:
                save_checkpoint(models, current_episode)
                save_record(data=records)

            if current_episode % (CHECK_POINT_INTERVAL * 5) == 0 and current_episode > 0:
                buffer.save_agent_buffer(current_episode)

    except KeyboardInterrupt:
        print("\n[DETECTED] Ctrl+C")
    except Exception as e:
        print(f"\n[ERROR] : {e}")
        raise e
    finally:
        # send_mail("Stop running","Please check")
        save_checkpoint(models, current_episode)
        save_record(data=records)
        writer.close()
        env.close()