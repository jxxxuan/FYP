import random
import torch
import os
from hyperparameter import *
from constants import *
from utils.utils import *
from bc import *
from start_carla import restart_carla_docker

@torch.no_grad()
def test(env, target_town, tasks, junctions, actor, current_episode, writer):
    tasks_in_town = tasks.get(target_town, [])
    if not tasks_in_town:
        return
    
    selected_task = random.choice(tasks_in_town)
    junction_name = selected_task['junction_name']
    junction_data = junctions[target_town].get('test_junctions', {}).get(junction_name, [])

    actual_actor = actor._orig_mod if hasattr(actor, "_orig_mod") else actor
    actual_actor.eval()
    
    video_path = os.path.join(RC_DIR, f"debug_{target_town}_ep{current_episode}.mp4")
    start, target = build_pose(selected_task)

    obs, _ = env.reset(target_town, level=0, junction_data=junction_data, start_transform=start, target_location=target, video_path=video_path)
    
    episode_reward = 0
    done = False
    step = 0
    
    while step < MAX_STEPS + (MAX_STEPS * 0.2) and not done:
        v_input, g_input = preprocess_obs(obs['visual'], obs['goal'], device)

        mu, _ = actual_actor(v_input, g_input)
        action = torch.tanh(mu)
        action_numpy = action.detach().cpu().numpy()[0]

        next_obs, reward, terminated, truncated, info = env.step(action_numpy)
        
        obs = next_obs
        episode_reward += reward
        step += 1
        done = terminated or truncated
            
    print(f"Test Run Reward: {episode_reward:.2f} | Steps: {step} | Reason: {info['reason']}")
    writer.add_scalar('Reward/Test', episode_reward, current_episode)

    actual_actor.train()

if __name__ == '__main__':
    for i in range(100):
        client = carla.Client(CARLA_HOST, int(CARLA_PORT))
        client.set_timeout(10.0)
        world = client.load_world('town04')

        