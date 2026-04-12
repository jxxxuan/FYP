import os
import sys
import pickle
import numpy as np
import carla
import json
import time
import cv2
import re

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from constants import ED_DIR, TRAIN_JSON, TEST_JSON
from envs.carla_env import CarlaEnv

def load_all_tasks(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def collect_data_from_json(json_path, target_town="Town03"):
    env = CarlaEnv(npc=True)
    all_data = load_all_tasks(json_path)
    
    towns = ['Town03', 'Town04', 'Town05'] if target_town == '*' else [target_town]

    for town in towns:
    # 加载任务
        town_data = all_data.get(town, {})

        for junction_name, junction_info in town_data.items():
            # 1. 为当前路口创建文件夹
            save_dir = os.path.join(ED_DIR, town, junction_name.replace(" ", "_"))
            os.makedirs(save_dir, exist_ok=True) # 确保文件夹存在

            existing_files = [f for f in os.listdir(save_dir) if f.endswith('.pkl')]
            if existing_files:
                # 提取文件名中的所有数字，取最大的一个
                existing_ids = [int(re.findall(r'\d+', f)[-1]) for f in existing_files if re.findall(r'\d+', f)]
                max_completed_id = max(existing_ids) if existing_ids else -1
            else:
                max_completed_id = -1

            print(f"\n>>> 路口 {junction_name}: 检测到最大完成 ID 为 {max_completed_id}")
            
            for task in junction_info['tasks']:
                # 2. 先定义 task_id，再拼接路径
                task_id = task['task_id']
                current_id_num = int(re.findall(r'\d+', str(task_id))[-1])

                # --- 断点续传判断 ---
                # 如果当前 ID 小于或等于已存在的最大 ID，彻底跳过（连 env.reset 都不进）
                if current_id_num <= max_completed_id:
                    continue
                save_file = os.path.join(save_dir, f"{task_id}.pkl")
                video_file = os.path.join(save_dir, f"{task_id}.mp4")
                
                # 如果文件已存在，跳过（断点续传功能）
                if os.path.exists(save_file):
                    print(f"任务 {task_id} 已存在，跳过...")
                    continue

                s = task['start_pose']
                t = task['target_pose']
                
                start_transform = carla.Transform(
                    carla.Location(x=s['x'], y=s['y'], z=s['z']), # 抬高防卡地
                    carla.Rotation(yaw=s['rotate'])
                )
                target_loc = carla.Location(x=t['x'], y=t['y'], z=t['z'])

                obs, _ = env.reset(video_path=video_file, start_transform=start_transform, target_location=target_loc, town=town)

                # 配置 Autopilot
                tm = env.client.get_trafficmanager(8000)
                path = [wp[0].transform.location for wp in env.route]
                tm.set_path(env.ego.vehicle, path)
                env.ego.vehicle.set_autopilot(True, 8000)
                
                temp_episode_data = [] # 每个任务独立的数据缓冲区
                success = False
                
                print(f"正在执行任务 {task_id} (距离: {task['distance']}m)...")
                
                for step in range(1500):
                    # time.sleep(0.01)
                    # 1. 直接从 Autopilot 获取专家动作 (Steer, Throttle, Brake)
                    control = env.ego.vehicle.get_control()
                    expert_action = np.array([control.steer, control.throttle, control.brake], dtype=np.float32)
                    
                    # 2. 调用标准的 step 方法
                    # 注意：即便 autopilot 已经控制了车，调用 apply_action 覆盖一次也是安全的
                    next_obs, reward, terminated, _, _ = env.step(expert_action)

                    # 3. 存储数据
                    temp_episode_data.append({
                        'obs': obs,
                        'action': expert_action,
                        'reward': reward,
                        'next_obs': next_obs,
                        'done': terminated
                    })
                    
                    obs = next_obs
                    
                    if terminated:
                        print('终止')
                        # 只有达到目标点才算真正成功
                        dist_curr = env.ego.get_location().distance(target_loc)
                        if dist_curr < 3.0:
                            success = True
                        break

                # 3. 只有成功完成的任务才保存
                env.stop_recording()
                if success:
                    with open(save_file, "wb") as f:
                        pickle.dump(temp_episode_data, f)
                    task['valid'] = True
                    print(f"   [保存] 数据与视频已存至 {save_dir}")
                else:
                    # 如果任务失败，删除刚才生成的视频文件，节省空间
                    if os.path.exists(video_file):
                        os.remove(video_file)
                    task['valid'] = False
                    print(f"   [舍弃] 任务失败，已清理视频")
                    
            with open(json_path, 'w') as f:
                json.dump(all_data, f, indent=4)
            print(f"路口 {junction_name} 处理完毕，进度已写入 JSON。")
    
if __name__ == "__main__":
    # 确保当前路径有 tasks.json
    try:
        collect_data_from_json(TEST_JSON, target_town="*")
    except Exception as e:
        import traceback
        traceback.print_exc()