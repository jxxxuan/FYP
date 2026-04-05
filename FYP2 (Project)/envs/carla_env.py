import gymnasium as gym
from gymnasium import spaces
import numpy as np
import carla
from dotenv import load_dotenv
import os
from envs.car import EgoVehicle
import time
import cv2
from collections import deque
import torch
import sys
from utils.CarlaPainter.carla_painter import CarlaPainter
from constants import IMG_DIM, FIXED_DELTA_SECONDS
load_dotenv()

host = os.getenv("CARLA_HOST")
carla_path = os.getenv("CARLA_API_PATH")

sys.path.append(carla_path)
from agents.navigation.global_route_planner import GlobalRoutePlanner

class CarlaEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.observation_space = spaces.Dict({
            "visual": spaces.Box(low=0, high=255, shape=(4, IMG_DIM, IMG_DIM, 3), dtype=np.uint8), # 4帧堆叠
            "goal": spaces.Box(low=-np.inf, high=np.inf, shape=(2,), dtype=np.float32)   # 目标向量
        })
        self.action_space = spaces.Box(low=np.array([-1, 0, 0]), high=np.array([1, 1, 1]), dtype=np.float32)
        self.client, self.world = self._connect_to_carla()
        settings = self.world.get_settings()
        settings.synchronous_mode = True
        settings.fixed_delta_seconds = FIXED_DELTA_SECONDS     
        settings.max_substep_delta_time = 0.02    
        settings.max_substeps = 10            
        self.world.apply_settings(settings)
        self.map = self.world.get_map()
        self.grp = GlobalRoutePlanner(self.map, 2.0)
        spawn_points = self.map.get_spawn_points()
        intersection_spawn_points = {'task1':[66,128,127,48,125,64,57,56],
                                    'task2':[168, 167, 179,180,178,177,5,6],
                                    'task3':[105,106,208,146,209],
                                    'task4':[104,103,101,102,182],
                                    'task5':[81,82,111],
                                    'task6':[234,236],}

        self.frame_stack = deque(maxlen=4) # 自动维护最近4帧
        self.target_location = carla.Location(x=100.0, y=20.0, z=0.0)
        # self.painter = CarlaPainter(host, 8081)
        # self._visualize_spawns()

    # def _visualize_spawns(self):
    #     sp = self.world.get_map().get_spawn_points()
    #     # 只画前 300 个，防止数据包太大导致 WebSocket 断开
    #     msgs = [str(i) for i in range(len(sp[:300]))]
    #     pos = [[p.location.x, p.location.y, p.location.z + 2.0] for p in sp[:300]]
    #     self.painter.draw_texts(msgs, pos, color='#FF0000', size=25)

    def _get_observation(self):
        # 1. 先获取队列中的完整数据包
        data_packet = self.ego.sensor_data['front_camera'].get(timeout=4)
        
        # 2. 检查数据包内容
        # 如果 data_packet 是 (frame, image_array)，则：
        frame, img = data_packet 
        
        # 3. 按照论文要求缩放至 img_dimximg_dim [cite: 167, 168]
        #resized_img = cv2.resize(img, (img_dim, img_dim))
        
        # 4. 实现 4 帧堆叠逻辑 
        while len(self.frame_stack) < 4:
            self.frame_stack.append(img)
        self.frame_stack.append(img)
        
        # 5. 获取 2 维目标向量 [cite: 191, 192]
        curr_loc = self.ego.get_location()

        # 找到路径中距离当前车位置最近的后续点（比如取前方第 5 个点）
        # 这样可以让模型学会有预见性的转向
        next_waypoint_idx = self._get_closest_waypoint_index(curr_loc)
        look_ahead_idx = min(next_waypoint_idx + 5, len(self.route) - 1)
        target_wp = self.route[look_ahead_idx][0]

        goal_vec = np.array([
            self.target_location.x - curr_loc.x,
            self.target_location.y - curr_loc.y
        ], dtype=np.float32)
        
        return {
            "visual": np.array(self.frame_stack), 
            "goal": goal_vec
        }
    
    def _get_closest_waypoint_index(self, curr_loc):
        # 设定一个搜索窗口，比如只看当前点之后的 20 个点
        search_range = 20
        start_idx = self.last_waypoint_index
        end_idx = min(start_idx + search_range, len(self.route))
        
        subset = self.route[start_idx : end_idx]
        
        # 如果路径快走完了，直接返回最后一个
        if not subset:
            return len(self.route) - 1

        distances = [curr_loc.distance(wp[0].transform.location) for wp in subset]
        min_idx_in_subset = np.argmin(distances)
        
        # 更新全局索引
        self.last_waypoint_index = start_idx + min_idx_in_subset
        return self.last_waypoint_index
    
    def _compute_reward(self, current_v, dist_pre, dist_curr, collided, offroad, reached):
        # 基础组件：Rc (碰撞), Rg (到达), Rd (距离), Rv (速度), Ror (车道) [cite: 202]
        if collided: return -100.0  # Rc [cite: 213]
        if reached: return 100.0    # Rg [cite: 219]
        
        r_v = current_v / 10.0      # Rv: velocity / 10 [cite: 217]
        r_d = dist_pre - dist_curr  # Rd: d_pre - d_cu [cite: 214]
        r_lane = -0.05 if offroad else 0.0 # Ror/Rol [cite: 218, 219]
        
        return r_v + r_d + r_lane

    def _check_done(self):
        return False  # 暂时永不结束
    
    def _connect_to_carla(self):
        client = carla.Client(host, 2000)
        client.set_timeout(60.0)
        world = client.load_world('Town03')
        client.reload_world()
        return client, world
    
    def reset(self, seed=None, options=None):
        if hasattr(self, 'ego') and self.ego is not None:
            self.ego.destroy()
            self.ego = None
            
        spawn_points = self.map.get_spawn_points()
        START_POINT_ID = 101
        TARGET_POINT_ID = 82
        
        start_pose = spawn_points[START_POINT_ID]
        target_pose = spawn_points[TARGET_POINT_ID]
        self.ego = EgoVehicle(self.world, start_pose)

        self.target_location = target_pose.location
        self.route = self.grp.trace_route(start_pose.location, target_pose.location)
        self.last_waypoint_index = 0
        self.ego.reset_flags() # 重置碰撞和压线状态
        self.world.tick()
        obs = self._get_observation()
        info = {}
        return obs, info
    
    def step(self, action):
        # 记录执行动作前的距离
        curr_loc = self.ego.get_location()
        dist_pre = curr_loc.distance(self.target_location)
        
        # 1. 执行动作 (加速, 转向, 制动)
        self._apply_action(action)
        self.world.tick()

        # 2. 获取新观察值
        obs = self._get_observation()
        
        # 3. 获取当前车辆状态用于奖励计算
        v = self.ego.get_velocity()
        speed = 3.6 * np.sqrt(v.x**2 + v.y**2 + v.z**2) / 3.6 # 转为 m/s [cite: 205]
        dist_curr = self.ego.get_location().distance(self.target_location)
        collided = self.ego.collision_flag # 需在 Ego 类实现该标志位
        offroad = self.ego.offroad_flag    # 需在 Ego 类实现该标志位
        reached = dist_curr < 2.0          # 到达目标的判定阈值

        # 4. 计算论文 Equation 7 的奖励
        reward = self._compute_reward(speed, dist_pre, dist_curr, collided, offroad, reached)
        
        # 5. 判定结束 [cite: 256]
        terminated = collided or reached
        truncated = False # 也可以根据步数设置
        
        return obs, reward, terminated, truncated, {}
    
    def render(self):
        pass
    
    def close(self):
        self.ego.destroy()
        settings = self.world.get_settings()
        settings.synchronous_mode = False
        self.world.apply_settings(settings)

    def _apply_action(self, action):
        # 如果 action 是 Tensor，先转到 cpu 并转为 numpy
        if torch.is_tensor(action):
            action = action.detach().cpu().numpy().flatten()
        
        # 现在可以安全地转为 float 了
        steer = float(action[0])
        throttle = float(action[1])
        brake = float(action[2])
        
        self.ego.apply_control(throttle=throttle, steer=steer, brake=brake)
        
if __name__ == '__main__':
    try:
        env = CarlaEnv()
        obs, info = env.reset()
        action = env.action_space.sample()
        #obs, reward, done, truncated, info = env.step(action)
    finally:
        env.close()
