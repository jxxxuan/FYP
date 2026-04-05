import os
import pickle
import numpy as np
import carla
from envs.carla_env import CarlaEnv
import time

def collect_data(total_episodes=50, frames_per_episode=500): # 建议增加步数，防止还没到就结束了
    env = CarlaEnv()
    expert_buffer = []

    for eps in range(total_episodes):
        obs, _ = env.reset()
        tm = env.client.get_trafficmanager(8000)
        
        # 路径强制规划
        path = [wp[0].transform.location for wp in env.route]
        tm.set_path(env.ego.vehicle, path)
        tm.auto_lane_change(env.ego.vehicle, True)
        
        # 开启 Autopilot
        env.ego.vehicle.set_autopilot(True, 8000) # 指定 TM 端口更稳
        
        temp_episode_data = [] # 暂存本回合数据
        success = False
        
        print(f"开始采集第 {eps+1} 个回合...")
        
        for step in range(frames_per_episode):
            env.world.tick() # 同步模式下驱动模拟器
            time.sleep(0.05)
            
            control = env.ego.vehicle.get_control()
            action = np.array([control.steer, control.throttle, control.brake], dtype=np.float32)
            
            next_obs = env._get_observation()
            
            # 计算物理信息
            v = env.ego.get_velocity()
            speed = 3.6 * np.sqrt(v.x**2 + v.y**2 + v.z**2) / 3.6
            dist_curr = env.ego.get_location().distance(env.target_location)
            
            # 判定状态
            reached = dist_curr < 2.5 # 终点判定
            collided = env.ego.collision_flag
            
            # 存入暂存区
            temp_episode_data.append({
                'obs': obs,
                'action': action,
                'reward': 1.0 if not collided else -100.0,
                'next_obs': next_obs,
                'done': collided or reached
            })

            obs = next_obs
            
            if reached:
                success = True
                print(f"--- 回合 {eps+1} 成功到达目的地！ ---")
                break
            if collided:
                print(f"--- 回合 {eps+1} 撞车，舍弃数据 ---")
                break
        
        # 只有成功到达的回合才存入大 Buffer
        if success:
            expert_buffer.extend(temp_episode_data)
            # 实时保存，防止崩溃
            with open("expert_data.pkl", "wb") as f:
                pickle.dump(expert_buffer, f)

    print(f"全部采集完成！总帧数: {len(expert_buffer)}")

if __name__ == "__main__":
    collect_data(1,1000)