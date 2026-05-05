import math
import time
import gymnasium as gym
from gymnasium import spaces
import numpy as np
import carla
from envs.car import EgoVehicle
import torch
from CarlaPainter.carla_painter import CarlaPainter
from constants import *
from hyperparameter import IMG_DIM_X, IMG_DIM_Y
from agents.navigation.global_route_planner import GlobalRoutePlanner
import os
import sys
import math

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from models.sac_agent import ObsBuffer

class CarlaEnv(gym.Env):
    def __init__(self, max_retries = 3):
        super().__init__()
        self.observation_space = spaces.Dict({
            "visual": spaces.Box(low=0, high=255, shape=(4, IMG_DIM_Y, IMG_DIM_X*2, 3), dtype=np.uint8), # 4帧堆叠
            "goal": spaces.Box(low=-np.inf, high=np.inf, shape=(2,), dtype=np.float32)   # 目标向量
        })
        self.action_space = spaces.Box(
            low=np.array([-1, -1]),
            high=np.array([1, 1]),
            dtype=np.float32
        )
        self._connect_to_carla()
        self.obs_buffer = ObsBuffer(stack=4)
        self.current_town = None
        self.max_retries = max_retries
        self.blueprints = [bp for bp in self.world.get_blueprint_library().filter('vehicle.*') 
                    if bp.get_attribute('base_type').as_str().lower() != 'bicycle']
        self.npc_list = []

    def _connect_to_carla(self):
        self.client = carla.Client(CARLA_HOST, int(CARLA_PORT))
        self.client.set_timeout(10.0)
        self.tm = self.client.get_trafficmanager(8000)
        self.tm.set_synchronous_mode(True)
        self.world = self.client.get_world()
    
    def _load_world(self, town="town03"):
        self.clean_npcs()
        if self.current_town == None or not town.lower() == self.current_town.lower():
            self.clean_ego()
            self.clean_world()
            for i in range(self.max_retries):
                try:
                    self.world = self.client.load_world(town)
                    break
                except RuntimeError:
                    print(f'Attempt {i+1} failed, retrying in 2s...')
                    time.sleep(1)
                    self.client.reload_world()
                    time.sleep(1)
            else:
                raise RuntimeError("Could not connect to CARLA after multiple retries.")
                
            self.current_town = town
            settings = self.world.get_settings()
            settings.synchronous_mode = True
            settings.fixed_delta_seconds = FIXED_DELTA_SECONDS     
            settings.max_substep_delta_time = SUBSTEP_DELTA
            settings.max_substeps = MAX_SUBSTEPS
            self.world.apply_settings(settings)
            self.map = self.world.get_map()
            self.grp = GlobalRoutePlanner(self.map, GRP)

    def set_ego_autopilot(self):
        self.tm.vehicle_percentage_speed_difference(self.ego.vehicle, 30.0)
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

        combined_img = np.concatenate([img_l, img_r], axis=1)

        img_debug = None
        if self.use_debug_cam:
            img_debug = self.ego.sensor_data['debug_camera'].get(timeout=2.0).copy()

        trans = self.ego.get_transform()
        loc = trans.location
        
        # 3. 向量化计算
        # 直接计算相对向量
        d_vec = np.array([self.target_location.x - loc.x, 
                        self.target_location.y - loc.y], dtype=np.float32)
        
        # 旋转计算 (使用预算的 sin/cos 会更快)
        rad = math.radians(-trans.rotation.yaw)
        c, s = math.cos(rad), math.sin(rad)
        
        # 旋转矩阵简写
        lx = d_vec[0] * c - d_vec[1] * s
        ly = d_vec[0] * s + d_vec[1] * c
        
        # 4. 归一化
        norm = math.sqrt(lx**2 + ly**2) + 1e-6
        goal_vec = np.array([lx/norm, ly/norm], dtype=np.float32)
        
        return combined_img, goal_vec, img_debug
    
    def _spawn_at_junction(self, end=True):
        # 只在标记为 start 的点尝试补车
        if not end:
            spoint = [p for p in self.current_junction_data if p.get('start')]
        else:
            spoint = self.current_junction_data

        for pt in spoint:
            tf = carla.Transform(carla.Location(x=pt['x'], y=pt['y'], z=pt['z']), 
                                carla.Rotation(yaw=pt['rotate']))
            blueprint = np.random.choice(self.blueprints)
            # try_spawn_actor 会自动处理碰撞检测，如果位置有车则返回 None
            vehicle = self.world.try_spawn_actor(blueprint, tf)
            if vehicle is not None:
                self._configure_npc_behavior(vehicle)
                self.npc_list.append(vehicle)

    def _configure_npc_behavior(self, vehicle):
        """提取出来的配置函数，保持代码整洁"""
        vehicle.set_autopilot(True, 8000)
        
        speed_min =  30.0 - (self.current_level * 40.0)
        self.tm.vehicle_percentage_speed_difference(vehicle, np.random.uniform(speed_min, speed_min + 20))
        self.tm.ignore_lights_percentage(vehicle, self.current_level * 50.0)
        self.tm.distance_to_leading_vehicle(vehicle, max(0.5, 3.0 - (self.current_level * 2.5)))
        lc_prob = self.current_level * 80.0
        self.tm.random_left_lanechange_percentage(vehicle, lc_prob)
        self.tm.random_right_lanechange_percentage(vehicle, lc_prob)
        offset = self.current_level * 0.8
        self.tm.vehicle_lane_offset(vehicle, np.random.uniform(-offset, offset))

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
    
    def _compute_reward(self, current_v, dist_pre, dist_curr, collided, offroad, otherlane, onmarking, reached, too_far):
        # --- 第一层：生死奖励 (Sparse Rewards) ---
        # 这里的惩罚需要比在原地等待500步的总和来的多吗
        if collided: return -100.0 
        if offroad: return -100.0
        if otherlane: return -100.0
        if reached: return 200.0   
        if too_far: return -50.0
        
        # --- 第二层：进度奖励 (Shaping Rewards) ---
        r_d = (dist_pre - dist_curr)
        # r_d = (dist_pre - dist_curr) * 10.0
        
        # --- 第三层：驾驶规范 (Fine-tuning Rewards) ---
        r_v = current_v / 10.0

        if current_v < 1.0:
            # 还是应该让原地等待500步的惩罚和sparse reward 一样多
            # r_v -= 100 / MAX_STEP
            r_v -= 0.5
         
        # r_or = -0.05 if offroad else 0.0
        # r_ol = -0.05 if otherlane else 0.0
        r_om = -0.5 if onmarking else 0.0
        
        # return r_v + r_d + r_or + r_ol
        return r_v + r_d + r_om

    def reset(self, town, level=0, junction_data=None, video_path=None, start_transform=None, target_location=None, ego_autopilot=False, seed=None, options=None):
        self._load_world(town)
        self.current_junction_data = junction_data # 保存路口数据
        self.current_level = level

        self.target_location = target_location
        self.current_step = 0
        self.route = self.grp.trace_route(start_transform.location, self.target_location)
        if hasattr(self, 'ego') and self.ego is not None:
            self.ego.teleport(start_transform)
        else:
            self.ego = EgoVehicle(self.world, start_transform)
            if ego_autopilot:
                self.set_ego_autopilot()
        
        self._spawn_at_junction()

        self.last_waypoint_index = 0
        self.ego.reset_flags() # 重置碰撞和压线状态

        self.start_distance = start_transform.location.distance(target_location)
        self.min_distance = self.start_distance

        self.obs_buffer.reset()
        self.video_path = video_path
        self.use_debug_cam = video_path and os.path.basename(video_path).startswith("debug")

        for _ in range(PRETICK_STEP):
            self.world.tick()
        raw_img, goal_vec, debug_img = self._get_observation()
        self.obs_buffer.add(
            visual=raw_img, 
            goal=goal_vec, 
            debug_frame=debug_img
        )

        info = {}
        return self.obs_buffer.get_current_obs(), info
    
    def step(self, action):
        dist_pre = self.ego.get_location().distance(self.target_location)

        self.ego.update_flags()
        self._apply_action(action)
        self.world.tick()

        v = self.ego.get_velocity()
        speed = np.sqrt(v.x**2 + v.y**2 + v.z**2) # 转为 m/s
        dist_curr = self.ego.get_location().distance(self.target_location)
        
        self.min_distance = min(self.min_distance, dist_curr)
        collided = self.ego.collision_flag 
        offroad = self.ego.offroad_flag    
        otherlane = self.ego.otherlane_flag
        onmarking = self.ego.on_marking_flag
        reached = dist_curr < 2.0          # 到达目标的判定阈值
        too_far = dist_curr > (self.start_distance + 25.0)

        # 4. 计算论文 Equation 7 的奖励
        reward = self._compute_reward(speed, dist_pre, dist_curr, collided, offroad, otherlane, onmarking, reached, too_far)

        raw_img, goal_vec, debug_img = self._get_observation()

        # 5. 判定结束 [cite: 256]
        terminated = collided or offroad or otherlane or reached or too_far
        truncated = self.current_step >= MAX_STEPS

        reason = None
        if terminated or truncated:
            if reached: reason = "R"
            elif collided: reason = "C"
            elif offroad: reason = "OR"
            elif otherlane: reason = "OL"
            elif too_far: reason = "TF"
            elif truncated: reason = "TO"

        # if self.current_step > 0 and self.current_step % 100 == 0:
        #     self._spawn_at_junction(end=False)

        self.obs_buffer.add(
            visual=raw_img, 
            goal=goal_vec, 
            action=action, 
            reward=reward, 
            terminate_reason=reason, # 必须传入这个参数！
            debug_frame=debug_img
        )

        # 在结束时释放资源
        if (terminated or truncated) and self.video_path is not None:
            os.makedirs(os.path.dirname(self.video_path), exist_ok=True)
            self.obs_buffer.to_video(self.video_path, fps=FPS)

        self.current_step += 1
        return self.obs_buffer.get_current_obs(), reward, terminated, truncated, {"reason": reason}

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

    def close(self):
        self.clean_npcs()
        self.clean_ego()
        self.clean_world()

    def clean_ego(self):
        if hasattr(self, 'ego') and self.ego is not None:
            self.ego.destroy()
            self.ego = None

    def clean_npcs(self):
        if not self.npc_list:
            return
            
        batch = [carla.command.DestroyActor(a) 
                for a in self.npc_list 
                if a is not None]
        if batch:
            self.client.apply_batch_sync(batch, False)
        
        self.npc_list = []

    def clean_world(self):
        if hasattr(self, 'world') and self.world is not None:
            settings = self.world.get_settings()
            settings.synchronous_mode = False
            self.world.apply_settings(settings)