import os
import sys
import pickle
import numpy as np
import carla
import json
import re

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from constants import ED_DIR, TRAIN_JSON, TEST_JSON
from envs.carla_env import CarlaEnv

def load_all_tasks(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def collect_data_from_json(json_path, repeat, target_town="Town03"):
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
                task_id = task['task_id']
                current_id_num = int(re.findall(r'\d+', str(task_id))[-1])

                if current_id_num <= max_completed_id:
                    continue

                levels = np.linspace(0, 0.7, repeat)
                for i, level in enumerate(levels):
                    print("Level: ", level)
                    save_file = os.path.join(save_dir, f"{task_id}_{i}.pkl")
                    video_file = os.path.join(save_dir, f"{task_id}_{i}.mp4")
                    
                    # 如果文件已存在，跳过（断点续传功能）
                    if os.path.exists(save_file):
                        print(f"任务 {task_id} 已存在，跳过...")
                        continue

                    s = task['start_pose']
                    t = task['target_pose']
                    
                    start_transform = carla.Transform(
                        carla.Location(x=s['x'], y=s['y'], z=s['z']),
                        carla.Rotation(yaw=s['rotate'])
                    )
                    target_loc = carla.Location(x=t['x'], y=t['y'], z=t['z'])

                    obs, _ = env.reset(video_path=video_file, level=level, start_transform=start_transform, target_location=target_loc, town=town)
                    
                    # 配置 Autopilot
                    env.set_autopilot()
                    
                    success = False

                    print(f"正在执行任务 {task_id} (距离: {task['distance']}m)...")
                    
                    for step in range(500):
                        try:
                            if not env.ego.vehicle.is_alive:
                                print(f"车辆已销毁，停止采集任务 {task_id}")
                                break
                            # 1. 直接从 Autopilot 获取专家动作 (Steer, Throttle, Brake)
                            control = env.ego.vehicle.get_control()
                            steer = control.steer
                            if control.brake > 0.1: # 稍微提高阈值，过滤掉 Autopilot 的微小抖动
                                acc = -float(control.brake)
                            elif control.throttle > 0.1:
                                acc = float(control.throttle)
                            else:
                                acc = 0.0 # 怠速状态，既不给油也不给刹
                            
                            expert_action = np.array([steer, acc], dtype=np.float32)
                        
                            _, _, terminated, _, _ = env.step(expert_action)
                            
                            if terminated:
                                print('终止')
                                # 只有达到目标点才算真正成功
                                dist_curr = env.ego.get_location().distance(target_loc)
                                if dist_curr < 2.0:
                                    success = True
                                break

                        except Exception as e:
                            print(f"任务 {task_id} 发生异常: {e}")
                            terminated = True  # 强制结束当前任务
                            success = False

                    if success:
                        compact_data = env.obs_buffer.pack_episode(success=True)
    
                        with open(save_file, "wb") as f:
                            pickle.dump(compact_data, f)
                            
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
        collect_data_from_json(TRAIN_JSON, repeat = 3, target_town="Town05")
        # collect_single_task(TRAIN_JSON, target_town="Town05", target_id="25")
    except Exception as e:
        import traceback
        traceback.print_exc()