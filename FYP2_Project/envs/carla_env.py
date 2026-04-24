import time

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
        self.client.set_timeout(60.0)
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
        img_l, img_r = None, None
        retry_count = 0
        while img_l is None and img_r is None and retry_count < 5:
            try:
                # 1. 获取三个视角的数据
                img_l = self.ego.sensor_data['left_camera'].get(timeout=2.0)
                img_r = self.ego.sensor_data['right_camera'].get(timeout=2.0)
            except:
                print(f"Warning: Camera queue empty, retrying {retry_count+1}/5...")
                retry_count += 1

        if img_l is None or img_r is None:
            raise RuntimeError("Camera sensor failed to provide data after 10 retries.")

        # 3. 水平拼接 (Left, Front, Right)
        combined_img = np.concatenate([img_l, img_r], axis=1)

        img_debug = None
        if self.use_debug_cam:
            img_debug = self.ego.sensor_data['debug_camera'].get(timeout=2.0).copy()
        
        # 5. 获取 2 维目标向量 [cite: 191, 192]
        curr_loc = self.ego.get_location()
        goal_vec = np.array([
            self.target_location.x - curr_loc.x,
            self.target_location.y - curr_loc.y
        ], dtype=np.float32)
        
        return combined_img, goal_vec, img_debug
    
    def _spawn_npcs(self, center_location, junction_data, radius=60.0, level=0):
        level = np.clip(level, 0.0, 1.0)
        
        # 1. 速度差异：level越高，车速越可能不按限速开 (甚至超速)
        # 论文设定限速30km/h，我们通过这个比例来微调 [cite: 208, 287]
        speed_diff = 30.0 - (level * 40.0) 
        self.tm.global_percentage_speed_difference(speed_diff)
        self.npc_list = []
        blueprints = self.world.get_blueprint_library().filter('vehicle.*')
        
        custom_spawn_points = []
        for pt in junction_data:
            # 你可以决定只在 start: true 的位置刷 NPC，或者全部刷
            # 这里建议全部刷，让路口更拥挤
            loc = carla.Location(x=pt['x'], y=pt['y'], z=pt['z']) # z轴稍微抬高防止掉进地板
            rot = carla.Rotation(yaw=pt['rotate'])
            custom_spawn_points.append(carla.Transform(loc, rot))

        np.random.shuffle(custom_spawn_points)

        for transform in custom_spawn_points:
            if len(self.npc_list) >= NUM_NPC: break
                
            blueprint = np.random.choice(blueprints)
            if blueprint.has_attribute('color'):
                color = np.random.choice(blueprint.get_attribute('color').recommended_values)
                blueprint.set_attribute('color', color)
            
            # 使用 try_spawn_actor 防止点位重叠导致崩溃
            vehicle = self.world.try_spawn_actor(blueprint, transform)
            if vehicle is not None:
                self._configure_npc_behavior(vehicle, level)
                self.npc_list.append(vehicle)
        
        if len(self.npc_list) < NUM_NPC:
            all_default_points = self.map.get_spawn_points()
            nearby_defaults = [sp for sp in all_default_points if sp.location.distance(center_location) < radius]
            np.random.shuffle(nearby_defaults)
            
            for sp in nearby_defaults:
                if len(self.npc_list) >= NUM_NPC: break
                # 检查这个默认点是否离我们已经生成的 NPC 太近，防止重叠
                blueprint = np.random.choice(blueprints)
                vehicle = self.world.try_spawn_actor(blueprint, sp)
                if vehicle is not None:
                    self._configure_npc_behavior(vehicle, level)
                    self.npc_list.append(vehicle)

        print(f"--- Spawned {len(self.npc_list)} NPCs (Custom + Defaults) ---")

    def _configure_npc_behavior(self, vehicle, level):
        """提取出来的配置函数，保持代码整洁"""
        vehicle.set_autopilot(True, 8000)
        vehicle.set_light_state(carla.VehicleLightState.LowBeam)
        
        # 你的各种 Level 惩罚/逻辑
        self.tm.ignore_lights_percentage(vehicle, level * 50.0)
        self.tm.distance_to_leading_vehicle(vehicle, max(0.5, 3.0 - (level * 2.5)))
        lc_prob = level * 80.0
        self.tm.random_left_lanechange_percentage(vehicle, lc_prob)
        self.tm.random_right_lanechange_percentage(vehicle, lc_prob)
        offset = level * 0.8
        self.tm.vehicle_lane_offset(vehicle, np.random.uniform(-offset, offset))

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
        if too_far: return -80.0
        
        # --- 第二层：进度奖励 (Shaping Rewards) ---
        r_d = (dist_pre - dist_curr) * 10.0
        # r_d = (dist_pre - dist_curr)
        
        # --- 第三层：驾驶规范 (Fine-tuning Rewards) ---
        r_v = current_v / 10.0

        if current_v < 2.0:
            r_v -= 0.5
         
        r_or = -0.5 if offroad else 0.0
        if offroad:
            print("offroad")
        # r_or = -0.05 if offroad else 0.0
        r_ol = -0.5 if otherlane else 0.0
        if otherlane:
            print("otherlane")
        # r_ol = -0.05 if otherlane else 0.0
        
        return r_v + r_d + r_or + r_ol

    def reset(self, town, level, junction_data=None, video_path=None, start_transform=None, target_location=None, seed=None, options=None):
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
        self.current_step = 0

        if self.npc:
            # 在 reset 方法的开头增加
            center_loc = carla.Location(
                x=(start_transform.location.x + target_location.x) / 2,
                y=(start_transform.location.y + target_location.y) / 2,
                z=start_transform.location.z
            )
            
            pts = junction_data if junction_data is not None else []
            self._spawn_npcs(center_loc, level=level, junction_data=pts)

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
        self.current_step += 1
        
        self.ego.update_flags()

        dist_pre = self.ego.get_location().distance(self.target_location)
        self._apply_action(action)
        # self._update_npc_lights()
        self.world.tick()
        time.sleep(0.25)

        # 3. 获取当前车辆状态用于奖励计算
        v = self.ego.get_velocity()
        speed = np.sqrt(v.x**2 + v.y**2 + v.z**2) # 转为 m/s [cite: 205]
        dist_curr = self.ego.get_location().distance(self.target_location)
        self.min_distance = min(self.min_distance, dist_curr)
        collided = self.ego.collision_flag 
        offroad = self.ego.offroad_flag    
        otherlane = self.ego.otherlane_flag
        reached = dist_curr < 2.0          # 到达目标的判定阈值
        if offroad:
            print("offroad")
        if otherlane:
            print("otherlane")

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
        truncated = self.current_step >= MAX_STEPS

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