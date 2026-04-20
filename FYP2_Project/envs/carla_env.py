import gymnasium as gym
from gymnasium import spaces
import numpy as np
import carla
from envs.car import EgoVehicle
import cv2
from collections import deque
import torch
from CarlaPainter.carla_painter import CarlaPainter
from hyperparameter import NUM_NPC
from constants import *
from hyperparameter import IMG_DIM_X, IMG_DIM_Y
from agents.navigation.global_route_planner import GlobalRoutePlanner
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from models.sac_agent import ObsBuffer

class CarlaEnv(gym.Env):
    def __init__(self, npc=False):
        super().__init__()
        self.observation_space = spaces.Dict({
            "visual": spaces.Box(low=0, high=255, shape=(4, IMG_DIM_Y, IMG_DIM_X*2, 3), dtype=np.uint8), # 4帧堆叠
            # "visual": spaces.Box(low=0, high=255, shape=(4, IMG_DIM_Y, IMG_DIM_X, 3), dtype=np.uint8), # 4帧堆叠
            "goal": spaces.Box(low=-np.inf, high=np.inf, shape=(2,), dtype=np.float32)   # 目标向量
        })
        # self.action_space = spaces.Box(
        #     low=np.array([-1.0, 0.0, 0.0], dtype=np.float32),  # 显式指定 float32
        #     high=np.array([1.0, 1.0, 1.0], dtype=np.float32), # 显式指定 float32
        #     dtype=np.float32
        # )
        self.action_space = spaces.Box(
            low=np.array([-1, -1]),
            high=np.array([1, 1]),
            dtype=np.float32
        )
        self._connect_to_carla()
        self.npc = npc
        self.obs_buffer = ObsBuffer(stack=4)
        self.current_town = None
        self.is_recording = False

    def _connect_to_carla(self):
        self.client = carla.Client(CARLA_HOST, int(CARLA_PORT))
        self.client.set_timeout(10.0)
        self.tm = self.client.get_trafficmanager(8000)
        self.tm.set_synchronous_mode(True)
    
    def _load_world(self, town):
        if self.current_town == None or not town.lower() == self.current_town.lower():
            self.world = self.client.load_world(town)
            self.current_town = town
            settings = self.world.get_settings()
            settings.synchronous_mode = True
            settings.fixed_delta_seconds = FIXED_DELTA_SECONDS     
            settings.max_substep_delta_time = SUBSTEP_DELTA
            settings.max_substeps = MAX_SUBSTEPS
            self.world.apply_settings(settings)
            self.map = self.world.get_map()
            self.grp = GlobalRoutePlanner(self.map, GRP)

    def set_autopilot(self):
        path = [wp[0].transform.location for wp in self.route]
        self.tm.set_path(self.ego.vehicle, path)
        self.ego.vehicle.set_autopilot(True, 8000)

    def _get_observation(self):
        
        # 1. 增加重试机制，防止队列暂时为空
        l_packet, r_packet = None, None
        retry_count = 0
        while l_packet is None and retry_count < 10:
            try:
                # 1. 获取三个视角的数据
                l_packet = self.ego.sensor_data['left_camera'].get(timeout=2.0)
                r_packet = self.ego.sensor_data['right_camera'].get(timeout=2.0)
            except:
                print(f"Warning: Camera queue empty, retrying {retry_count+1}/10...")
                retry_count += 1

        if l_packet is None or r_packet is None:
            raise RuntimeError("Camera sensor failed to provide data after 10 retries.")
        
        debug_img = None
        if self.use_debug_cam:
            debug_img = self.ego.sensor_data['debug_camera'].get(timeout=2.0)


        # 2. 提取图像 (假设只要 RGB 数组)
        img_l = l_packet[1]
        img_r = r_packet[1]

        # 3. 水平拼接 (Left, Front, Right)
        combined_img = np.concatenate([img_l, img_r], axis=1)
        
        # 5. 获取 2 维目标向量 [cite: 191, 192]
        curr_loc = self.ego.get_location()
        goal_vec = np.array([
            self.target_location.x - curr_loc.x,
            self.target_location.y - curr_loc.y
        ], dtype=np.float32)
        
        return combined_img, goal_vec, debug_img
    
    def _spawn_npcs(self, center_location, radius=60.0, level=0):
        level = np.clip(level, 0.0, 1.0)
        
        # 1. 速度差异：level越高，车速越可能不按限速开 (甚至超速)
        # 论文设定限速30km/h，我们通过这个比例来微调 [cite: 208, 287]
        speed_diff = 30.0 - (level * 40.0) 
        self.tm.global_percentage_speed_difference(speed_diff)
        self.npc_list = []
        blueprints = self.world.get_blueprint_library().filter('vehicle.*')
        
        # 1. 筛选距离路口中心较近的生成点
        all_spawn_points = self.map.get_spawn_points()
        nearby_spawn_points = []
        
        for sp in all_spawn_points:
            if sp.location.distance(center_location) < radius:
                nearby_spawn_points.append(sp)
        
        print(f"Found {len(nearby_spawn_points)} available spawn points")
        
        # 2. 如果附近点位不够，自动调整生成数量，防止挤在同一个点报错
        actual_spawn_num = min(NUM_NPC, len(nearby_spawn_points))
        np.random.shuffle(nearby_spawn_points)

        for i in range(actual_spawn_num):
            blueprint = np.random.choice(blueprints)
            # 论文提到包含不同车型 [cite: 252, 253]
            if blueprint.has_attribute('color'):
                color = np.random.choice(blueprint.get_attribute('color').recommended_values)
                blueprint.set_attribute('color', color)
            
            vehicle = self.world.try_spawn_actor(blueprint, nearby_spawn_points[i])
            if vehicle is not None:
                vehicle.set_autopilot(True, 8000)

                vehicle.set_light_state(carla.VehicleLightState.LowBeam)
                # 针对路口优化：让 NPC 稍微开快一点，增加博弈难度
                self.tm.vehicle_lane_offset(vehicle, np.random.uniform(-0.5, 0.5))
                # 2. 忽略红绿灯概率 (0% 到 50%)
                self.tm.ignore_lights_percentage(vehicle, level * 50.0)
                
                # 3. 忽略跟车距离 (Level越高，跟车越近，从3.0m减小到0.5m)
                min_dist = max(0.5, 3.0 - (level * 2.5))
                self.tm.distance_to_leading_vehicle(vehicle, min_dist)
                
                # 4. 变道频率 (0% 到 80%)
                lc_prob = level * 80.0
                self.tm.random_left_lanechange_percentage(vehicle, lc_prob)
                self.tm.random_right_lanechange_percentage(vehicle, lc_prob)
                
                # 5. 压线/偏移驾驶 (0.0 到 0.8)
                offset = level * 0.8
                self.tm.vehicle_lane_offset(vehicle, np.random.uniform(-offset, offset))
                self.npc_list.append(vehicle)

        print(f"Generated {len(self.npc_list)} NPC")

    def _update_npc_lights(self):
        for npc in self.npc_list:
            if not npc.is_alive: continue # 防止操作已销毁的 actor
            
            control = npc.get_control()
            new_lights = carla.VehicleLightState.LowBeam

            # 1. 动态刹车灯 (复刻 ViT 捕捉减速特征的关键)
            if control.brake > 0.1:
                new_lights |= carla.VehicleLightState.Brake
                
            # 2. 动态转向灯 (帮助识别横向侵入)
            if control.steer > 0.1:
                new_lights |= carla.VehicleLightState.RightBlinker
            elif control.steer < -0.1:
                new_lights |= carla.VehicleLightState.LeftBlinker
                
            npc.set_light_state(carla.VehicleLightState(new_lights))

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
    
    def _compute_reward(self, current_v, dist_pre, dist_curr, collided, offroad, otherlane, reached, too_far):
        # --- 第一层：生死奖励 (Sparse Rewards) ---
        if collided: return -100.0 
        if reached: return 100.0   
        if too_far: return -100.0
        
        # --- 第二层：进度奖励 (Shaping Rewards) ---
        # r_d = (dist_pre - dist_curr) * 50.0
        r_d = (dist_pre - dist_curr) * 10.0
        
        # --- 第三层：驾驶规范 (Fine-tuning Rewards) ---
        r_v = current_v / 10.0

        if current_v < 2.0:
            r_v -= 0.5
         
        
        # r_or = -10 if offroad else 0.0
        r_or = -0.05 if offroad else 0.0
        # r_ol = -2 if otherlane else 0.0
        r_ol = -0.05 if otherlane else 0.0
        
        return r_v + r_d + r_or + r_ol

    def reset(self, town, level, video_path=None, start_transform=None, target_location=None, seed=None, options=None):
        # 1. 清理旧车辆
        if hasattr(self, 'ego') and self.ego is not None:
            self.ego.destroy()
            self.ego = None

        if hasattr(self, 'npc_list') and self.npc_list:
                for npc in self.npc_list:
                    if npc is not None and npc.is_alive:
                        npc.destroy()
                self.npc_list = []

        self._load_world(town)
            
        start_pose = start_transform
        self.target_location = target_location

        # 3. 生成车辆
        # 注意：如果 start_pose 是从 JSON 读出来的，确保它是一个 carla.Transform 对象
        self.ego = EgoVehicle(self.world, start_pose)

        if self.npc:
            # 在 reset 方法的开头增加
            center_loc = carla.Location(
                x=(start_transform.location.x + target_location.x) / 2,
                y=(start_transform.location.y + target_location.y) / 2,
                z=start_transform.location.z
            )
            
            # 调用局部生成函数
            self._spawn_npcs(center_loc, level=level)

        self.route = self.grp.trace_route(start_pose.location, self.target_location)
        
        # 5. 状态重置
        self.last_waypoint_index = 0
        self.ego.reset_flags() # 重置碰撞和压线状态

        self.start_distance = start_transform.location.distance(target_location)
        # 记录过程中的历史最短距离（用于更严苛的判定）
        self.min_distance = self.start_distance

        # 6. 推进模拟器并获取观察值
        self.world.tick()

        self.obs_buffer.reset()
        self.video_path = video_path
        self.use_debug_cam = video_path and os.path.basename(video_path).startswith("debug")

        raw_img, goal_vec, debug_img = self._get_observation()
        
        self.obs_buffer.add(visual=raw_img, goal=goal_vec, debug_frame=debug_img)
        info = {}
        return self.obs_buffer.get_current_obs(), info
    
    def step(self, action):
        # 记录执行动作前的距离
        dist_pre = self.ego.get_location().distance(self.target_location)
        self._apply_action(action)
        # self._update_npc_lights()
        self.world.tick()

        # 3. 获取当前车辆状态用于奖励计算
        v = self.ego.get_velocity()
        speed = np.sqrt(v.x**2 + v.y**2 + v.z**2) # 转为 m/s [cite: 205]
        dist_curr = self.ego.get_location().distance(self.target_location)
        self.min_distance = min(self.min_distance, dist_curr)
        collided = self.ego.collision_flag # 需在 Ego 类实现该标志位
        offroad = self.ego.offroad_flag    # 需在 Ego 类实现该标志位
        otherlane = self.ego.otherlane_flag
        reached = dist_curr < 2.0          # 到达目标的判定阈值

        too_far = dist_curr > (self.start_distance + 25.0)

        # 4. 计算论文 Equation 7 的奖励
        reward = self._compute_reward(speed, dist_pre, dist_curr, collided, offroad, otherlane, reached, too_far)

        raw_img, goal_vec, debug_img = self._get_observation()

        self.obs_buffer.add(
            visual=raw_img, 
            goal=goal_vec, 
            action=action, 
            reward=reward, 
            debug_frame=debug_img
        )

        # 5. 判定结束 [cite: 256]
        terminated = collided or reached or too_far
        truncated = False # 也可以根据步数设置

        # 在结束时释放资源
        if (terminated or truncated):
            if self.video_path is not None:
                os.makedirs(os.path.dirname(self.video_path), exist_ok=True)
                self.obs_buffer.to_video(self.video_path, fps=FPS)
        
        return self.obs_buffer.get_current_obs(), reward, terminated, truncated, {}

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
        acc = float(action[1])
        if acc >= 0.1:
            throttle = acc
            brake = 0.0
        elif acc < -0.1:
            throttle = 0.0
            brake = -acc
        else:
            throttle = 0.0
            brake = 0.0
        
        self.ego.apply_control(throttle=throttle, steer=steer, brake=brake)