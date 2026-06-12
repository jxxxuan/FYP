import os
import sys
import pickle
import time
import numpy as np
import carla
import json
import re


current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from constants import ED_DIR, TRAIN_JSON, TEST_JSON, MAX_STEPS, INTESECTION_JSON
from envs.carla_env import CarlaEnv
from carla_server import start_carla, stop_carla

def load_all_tasks(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def collect_data_from_json(json_path, repeat, target_town="Town04"):
    
    all_data = load_all_tasks(json_path)
    
    towns = ['Town03', 'Town04', 'Town05'] if target_town == '*' else [target_town]
    # towns = ['Town04', 'Town05'] if target_town == '*' else [target_town]

    for town in towns:
        env = CarlaEnv(town=town)
        town_data = all_data.get(town, {})

        for junction_name, junction_info in town_data.items():
            # 1. Create a folder for the current junction
            save_dir = os.path.join(ED_DIR, town, junction_name.replace(" ", "_"))
            os.makedirs(save_dir, exist_ok=True) # Ensure folder exists

            existing_files = [f for f in os.listdir(save_dir) if f.endswith('.pkl')]
            if existing_files:
                # Extract all numbers from filename, get the maximum one
                existing_ids = [int(re.findall(r'\d+', f)[-1]) for f in existing_files if re.findall(r'\d+', f)]
                max_completed_id = max(existing_ids) if existing_ids else -1
            else:
                max_completed_id = -1

            print(f"\n>>> Junction {junction_name}: Detected max completed ID is {max_completed_id}")
            with open(INTESECTION_JSON, 'r') as f:
                junctions = json.load(f)
            junction_data = junctions[town].get('train_junctions', {}).get(junction_name, [])
            
            for task in junction_info['tasks']:
                task_id = task['task_id']
                current_id_num = int(re.findall(r'\d+', str(task_id))[-1])

                if current_id_num <= max_completed_id:
                    continue

                levels = np.linspace(0, 0.7, repeat)
                for i, level in enumerate(levels):
                    print("Level: ", level)
                    save_file = os.path.join(save_dir, f"{task_id}_{i}.pkl")
                    video_file = os.path.join(save_dir, f"{task_id}_{i}.mp4")
                    
                    # If file already exists, skip (breakpoint resume capability)
                    if os.path.exists(save_file):
                        print(f"Task {task_id} already exists, skipping...")
                        continue

                    s = task['start_pose']
                    t = task['target_pose']
                    
                    start_transform = carla.Transform(
                        carla.Location(x=s['x'], y=s['y'], z=s['z']),
                        carla.Rotation(yaw=s['rotate'])
                    )
                    target_loc = carla.Location(x=t['x'], y=t['y'], z=t['z'])
                    try:
                        obs, _ = env.reset(town=town, junction_data=junction_data ,video_path=video_file, level=level, start_transform=start_transform, target_location=target_loc)
                        env.set_ego_autopilot()

                        success = False

                        print(f"Executing task {task_id} (Distance: {task['distance']}m)...")
                        
                        for _ in range(MAX_STEPS):
                            if not hasattr(env, 'ego'):
                                print(f"Vehicle destroyed, stopping collection for task {task_id}")
                                break
                            # 1. Direct retrieval of expert action from Autopilot (Steer, Throttle, Brake)
                            control = env.ego.vehicle.get_control()
                            steer = control.steer
                            
                            t = float(control.throttle)
                            b = float(control.brake)

                            # 3. Perfect inverse mathematical mapping (inverse operation of _apply_action)
                            if b > 0.0:
                                # If there is braking, acc must be negative. Inverse scaling restoration:
                                # Since forward is b = (-acc - 0.05) / 0.95 -> Inverse calculation:
                                acc = -(b * 0.95 + 0.05)
                            elif t > 0.0:
                                # If there is throttle, acc must be positive. Inverse scaling restoration:
                                # Since forward is t = (acc - 0.05) / 0.95 -> Inverse calculation:
                                acc = t * 0.95 + 0.05
                            else:
                                # Expert applied neither throttle nor brake (coasting)
                                acc = 0.0
                            
                            expert_action = np.array([steer, acc], dtype=np.float32)
                        
                            next_obs, _, terminated, truncated, _ = env.step(expert_action)
                            
                            if terminated or truncated:
                                # Only reaching the target point counts as true success
                                dist_curr = env.ego.get_location().distance(target_loc)
                                if dist_curr < 2.0:
                                    success = True
                                break

                    except Exception as e:
                        print(f"Exception occurred in task {task_id}: {e}")
                        terminated = True  # Force terminate current task
                        success = False

                    if success:
                        compact_data = env.obs_buffer.pack_episode()
                        print("Total reward: ", compact_data['rewards'].sum())
    
                        with open(save_file, "wb") as f:
                            pickle.dump(compact_data, f)
                            
                        task['valid'] = True
                        print(f"   [Save] Data and video saved to {save_dir}")
                    else:
                        # If task fails, delete the generated video file to save space
                        task['valid'] = False
                        print(f"   [Discard] Task failed")
            
            with open(json_path, 'w') as f:
                json.dump(all_data, f, indent=4)
            print(f"Junction {junction_name} processed, progress written to JSON.")
        env.close()

if __name__ == "__main__":
    # Ensure tasks.json exists in the current path
    start_carla()
    try:
        collect_data_from_json(TRAIN_JSON, repeat = 3, target_town="Town03")
        collect_data_from_json(TRAIN_JSON, repeat = 3, target_town="Town04")
        collect_data_from_json(TRAIN_JSON, repeat = 3, target_town="Town05")
        # collect_data_from_json(TRAIN_JSON, repeat = 2, target_town="*")
        # collect_single_task(TRAIN_JSON, target_town="Town05", target_id="25")
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        # stop_carla()
        pass