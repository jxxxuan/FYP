import gymnasium as gym
from gymnasium import spaces
import numpy as np
import carla
from dotenv import load_dotenv
import os
from car import EgoVehicle
import time
import queue
import cv2

load_dotenv()

host = os.getenv("CARLA_HOST")
carla_path = os.getenv("CARLA_API_PATH")

class CarlaEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.observation_space = spaces.Box(low=0, high=255, shape=(84, 84, 3), dtype=np.uint8)  # 例子
        self.action_space = spaces.Box(low=np.array([-1, 0]), high=np.array([1, 1]), dtype=np.float32)  # 例子: [-1,1]方向盘, [0,1]油门
        self.client, self.world = self._connect_to_carla()
        settings = self.world.get_settings()
        settings.synchronous_mode = True
        settings.fixed_delta_seconds = 0.05       # 每步 0.05 秒
        settings.max_substep_delta_time = 0.05    # 每个物理子步 0.05 秒
        settings.max_substeps = 2                 # 总共 0.1 秒 > fixed_delta_seconds
        self.world.apply_settings(settings)
        spawn_points = self.world.get_map().get_spawn_points()
        start_pose = spawn_points[0]   # 起点
        self.ego = EgoVehicle(self.world, start_pose)

    def _get_observation(self):
        world_frame = self.world.get_snapshot().frame  # 当前tick的frame_id
        frame, img = None, None

        # 循环直到拿到当前tick对应的帧
        while frame != world_frame:
            frame, img = self.ego.sensor_data['front_camera'].get(timeout=4)
            img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            cv2.imwrite("output.png", img_bgr)  # 保存为 PNG
        return img
    
    def _compute_reward(self):
        return 0.0  # 暂时先返回0

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
