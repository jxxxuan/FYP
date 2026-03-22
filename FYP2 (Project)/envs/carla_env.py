import gymnasium as gym
from gymnasium import spaces
import numpy as np
import carla
from dotenv import load_dotenv
import os
from envs.car import EgoVehicle
import time
import cv2
from reward_functions import _compute_reward
from collections import deque

load_dotenv()

host = os.getenv("CARLA_HOST")
carla_path = os.getenv("CARLA_API_PATH")

class CarlaEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.observation_space = spaces.Dict({
            "visual": spaces.Box(low=0, high=255, shape=(4, 84, 84, 3), dtype=np.uint8), # 4帧堆叠
            "goal": spaces.Box(low=-np.inf, high=np.inf, shape=(2,), dtype=np.float32)   # 目标向量
        })
        self.action_space = spaces.Box(low=np.array([-1, 0, 0]), high=np.array([1, 1, 1]), dtype=np.float32)
        self.client, self.world = self._connect_to_carla()
        settings = self.world.get_settings()
        settings.synchronous_mode = True
        settings.fixed_delta_seconds = 0.2       # 每步 0.05 秒
        settings.max_substep_delta_time = 0.05    # 每个物理子步 0.05 秒
        settings.max_substeps = 2                 # 总共 0.1 秒 > fixed_delta_seconds
        self.world.apply_settings(settings)
        spawn_points = self.world.get_map().get_spawn_points()
        start_pose = spawn_points[0]   # 起点
        self.ego = EgoVehicle(self.world, start_pose)
        self.frame_stack = deque(maxlen=4) # 自动维护最近4帧
        self.target_location = carla.Location(...) # 论文中的目的地坐标

    def _get_observation(self):
        # 1. 从 EgoVehicle 获取并 resize 图像为 84x84 (需在 Ego 类中实现)
        _, img = self.ego.sensor_data['front_camera'].get(timeout=4)
        resized_img = cv2.resize(img, (84, 84))
        
        # 2. 填充队列实现 4 帧堆叠
        while len(self.frame_stack) < 4:
            self.frame_stack.append(resized_img)
        self.frame_stack.append(resized_img)
        
        # 3. 计算目标向量 [X_goal - X_av, Y_goal - Y_av]
        curr_loc = self.ego.get_location()
        goal_vec = np.array([
            self.target_location.x - curr_loc.x,
            self.target_location.y - curr_loc.y
        ], dtype=np.float32)
        
        return {
            "visual": np.array(self.frame_stack), 
            "goal": goal_vec
        }
    
    def _compute_reward(self, current_v, dist_pre, dist_curr, collided, offroad, reached):
        _compute_reward()

    def _check_done(self):
        return False  # 暂时永不结束
    
    def _connect_to_carla(self):
        client = carla.Client(host, 2000)
        client.set_timeout(10.0)
        world = client.load_world('Town04')
        return client, world
    
    def reset(self, seed=None, options=None):
        self.world.tick()
        obs = self._get_observation()
        info = {}
        return obs, info
    
    def step(self, action):
        # 执行动作
        self._apply_action(action)
        self.world.tick()

        obs = self._get_observation()
        while obs is None:
            # 获取状态
            obs = self._get_observation()
            time.sleep(0.001)
        
        # 计算奖励
        reward = self._compute_reward()
        
        # 是否结束
        terminated = self._check_done()
        truncated = False
        
        info = {}
        return obs, reward, terminated, truncated, info
    
    def render(self):
        pass
    
    def close(self):
        self.ego.destroy()
        settings = self.world.get_settings()
        settings.synchronous_mode = False
        self.world.apply_settings(settings)


if __name__ == '__main__':
    try:
        env = CarlaEnv()
        obs, info = env.reset()
        action = env.action_space.sample()
        #obs, reward, done, truncated, info = env.step(action)
    finally:
        env.close()
