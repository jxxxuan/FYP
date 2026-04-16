import gymnasium as gym
from gymnasium import spaces
import numpy as np
import carla
from envs.car import EgoVehicle
import time
import cv2
from collections import deque
import torch
from CarlaPainter.carla_painter import CarlaPainter
from hyperparameter import NUM_NPC
from constants import DEBUG_IMG_DIM_X, DEBUG_IMG_DIM_Y, FIXED_DELTA_SECONDS, CARLA_HOST, CARLA_PORT
from hyperparameter import IMG_DIM_X, IMG_DIM_Y
from agents.navigation.global_route_planner import GlobalRoutePlanner
import os

class CarlaEnv(gym.Env):
    def __init__(self, npc=False):
        super().__init__()
        self.observation_space = spaces.Dict({
            # "visual": spaces.Box(low=0, high=255, shape=(4, IMG_DIM_Y, IMG_DIM_X*2, 3), dtype=np.uint8), # 4帧堆叠
            "visual": spaces.Box(low=0, high=255, shape=(4, IMG_DIM_Y, IMG_DIM_X, 3), dtype=np.uint8), # 4帧堆叠
            "goal": spaces.Box(low=-np.inf, high=np.inf, shape=(2,), dtype=np.float32)   # 目标向量
        })
        self.action_space = spaces.Box(
            low=np.array([-1.0, 0.0, 0.0], dtype=np.float32),  # 显式指定 float32
            high=np.array([1.0, 1.0, 1.0], dtype=np.float32), # 显式指定 float32
            dtype=np.float32
        )
        # self.action_space = spaces.Box(
        #     low=np.array([-1, -1]),
        #     high=np.array([1, 1]),
        #     dtype=np.float32
        # )
        self._connect_to_carla()
        self.npc = npc
        self.frame_stack = deque(maxlen=4) # 自动维护最近4帧
        self.current_town = None
        self.video_writer = None
        self.is_recording = False
        # self.painter = CarlaPainter(host, 8081)
        # self._visualize_spawns()

    # def _visualize_spawns(self):
    #     sp = self.world.get_map().get_spawn_points()
    #     # 只画前 300 个，防止数据包太大导致 WebSocket 断开
    #     msgs = [str(i) for i in range(len(sp[:300]))]
    #     pos = [[p.location.x, p.location.y, p.location.z + 2.0] for p in sp[:300]]
    #     self.painter.draw_texts(msgs, pos, color='#FF0000', size=25)

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
            settings.max_substep_delta_time = 0.02
            settings.max_substeps = 10
            self.world.apply_settings(settings)
            self.map = self.world.get_map()
            self.grp = GlobalRoutePlanner(self.map, 2.0)

    '''def _get_observation(self):
        # 1. 增加重试机制，防止队列暂时为空
        f_packet, l_packet, r_packet = None, None, None
        retry_count = 0
        while l_packet is None and retry_count < 10:
            try:
                # 1. 获取三个视角的数据
                # f_packet = self.ego.sensor_data['front_camera'].get(timeout=2.0)
                l_packet = self.ego.sensor_data['left_camera'].get(timeout=2.0)
                r_packet = self.ego.sensor_data['right_camera'].get(timeout=2.0)
            except:
                print(f"Warning: Camera queue empty, retrying {retry_count+1}/10...")
                retry_count += 1

        if l_packet is None or r_packet is None:
            raise RuntimeError("Camera sensor failed to provide data after 10 retries.")

        # 2. 提取图像 (假设只要 RGB 数组)
        # img_f = f_packet[1]
        img_l = l_packet[1]
        img_r = r_packet[1]

        # 3. 水平拼接 (Left, Front, Right)
        combined_img = np.concatenate([img_l, img_r], axis=1) # 形状变为 (H, W*3, 3)
        
        # 4. 实现 4 帧堆叠逻辑 
        if len(self.frame_stack) == 0:
            for _ in range(4):
                self.frame_stack.append(combined_img)
        else:
            # 正常运行阶段，只添加最新的一帧
            # deque(maxlen=4) 会自动弹出最旧的一帧 (t-4)
            self.frame_stack.append(combined_img)
        
        # 5. 获取 2 维目标向量 [cite: 191, 192]
        curr_loc = self.ego.get_location()
        goal_vec = np.array([
            self.target_location.x - curr_loc.x,
            self.target_location.y - curr_loc.y
        ], dtype=np.float32)
        
        return {
            "visual": np.array(self.frame_stack, dtype=np.uint8), 
            "goal": goal_vec
        }'''
    
    def _get_observation(self):
        # 获取前向摄像头数据
        if self.ego is None or not self.ego.is_alive:
            raise RuntimeError("Ego vehicle was destroyed during the simulation.")
    
        packet = self.ego.sensor_data['front_camera'].get(timeout=2.0)
        img = packet # 应该是 (84, 84, 3)

        # 4 帧堆叠逻辑 
        self.frame_stack.append(img)
        while len(self.frame_stack) < 4:
            self.frame_stack.append(img)
        
        # 获取 2 维目标向量 
        curr_loc = self.ego.get_location()
        goal_vec = np.array([
            self.target_location.x - curr_loc.x,
            self.target_location.y - curr_loc.y
        ], dtype=np.float32)
        
        return {
            "visual": np.array(self.frame_stack, dtype=np.uint8), 
            "goal": goal_vec
        }
    
    def _spawn_npcs(self, center_location, number_of_vehicles=120, radius=60.0):
        """
        center_location: 当前路口的中心位置 (carla.Location)
        radius: 生成半径，120米左右能覆盖路口周围的所有支路
        """
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
        actual_spawn_num = min(number_of_vehicles, len(nearby_spawn_points))
        np.random.shuffle(nearby_spawn_points)

        tm = self.client.get_trafficmanager(8000)

        for i in range(actual_spawn_num):
            blueprint = np.random.choice(blueprints)
            # 论文提到包含不同车型 [cite: 252, 253]
            if blueprint.has_attribute('color'):
                color = np.random.choice(blueprint.get_attribute('color').recommended_values)
                blueprint.set_attribute('color', color)
            
            vehicle = self.world.try_spawn_actor(blueprint, nearby_spawn_points[i])
            if vehicle is not None:
                vehicle.set_autopilot(True, 8000)
                # 针对路口优化：让 NPC 稍微开快一点，增加博弈难度
                tm.vehicle_lane_offset(vehicle, np.random.uniform(-0.5, 0.5))
                self.npc_list.append(vehicle)
        
        print(f"Generated {len(self.npc_list)} NPC")

    def npc_action_randomize(self):
        for npc in self.npc_list:
            # 1. 设置超速/限速百分比（负数代表超速，正数代表限速）
            # 论文中提到车辆速度限制在 30km/h [cite: 208, 287]
            self.tm .vehicle_lane_offset(npc, np.random.uniform(-0.5, 0.5)) # 随机偏移，模拟不规整驾驶
            self.tm .global_percentage_speed_difference(30.0) # 全局限速 30%

            # 2. 忽略红绿灯（模拟鲁莽驾驶）
            self.tm .ignore_lights_percentage(npc, 20.0) # 20% 的概率闯红灯

            # 3. 忽略跟车距离（增加碰撞风险）
            self.tm .distance_to_leading_vehicle(npc, 1.0) # 强制跟车距离为 1 米

            # 4. 强制变道倾向
            self.tm .random_left_lanechange_percentage(npc, 50.0)
            self.tm .random_right_lanechange_percentage(npc, 50.0)
    
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
    
    '''def _compute_reward(self, current_v, dist_pre, dist_curr, collided, offroad, otherlane, reached):
        # 1. 碰撞惩罚 (Rc)
        if collided: 
            return -100.0  # 
        
        # 2. 到达奖励 (Rg)
        if reached: 
            return 100.0   # 
        
        # 3. 速度奖励 (Rv)
        # 论文设定速度限制为 30km/h (即 30/10=3) [cite: 208]
        target_speed = 8.0 
        r_v = current_v / target_speed
        
        # 4. 进度奖励 (Rd)
        r_d = (dist_pre - dist_curr) * 5
        
        # 5. 车道偏离惩罚 (Ror 和 Rol)
        r_or = -0.01 if offroad else 0.0    # [cite: 218]
        r_ol = -0.01 if otherlane else 0.0  # 

        if current_v < 1.0:
            r_slow = -0.2
        else:
            r_slow = 0
        
        return r_v + r_d + r_or + r_ol + r_slow'''
    
    def _compute_reward(self, current_v, dist_pre, dist_curr, collided, offroad, otherlane, reached):
        if collided: return -100.0 
        if reached: return 100.0   
        
        r_v = current_v / 10.0      # 论文设定 
        r_d = dist_pre - dist_curr  # 论文设定，无系数 
        
        # 论文设定为固定惩罚 -0.05 
        r_or = -0.05 if offroad else 0.0
        r_ol = -0.05 if otherlane else 0.0
        
        return r_v + r_d + r_or + r_ol

    def reset(self, town, video_path=None, start_transform=None, target_location=None, seed=None, options=None):
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
            self._spawn_npcs(center_loc)

        self.route = self.grp.trace_route(start_pose.location, self.target_location)
        
        # 5. 状态重置
        self.last_waypoint_index = 0
        self.ego.reset_flags() # 重置碰撞和压线状态
        
        self.is_recording = video_path is not None
        self.use_debug_cam = False
        if self.is_recording:
            filename = os.path.basename(video_path).lower()
            # 判定是否录制 debug 画面
            self.use_debug_cam = filename.startswith("debug")
            os.makedirs(os.path.dirname(video_path), exist_ok=True)
            
            # 初始化录制器 (20 FPS, 分辨率 IMG_DIM*3 x IMG_DIM)
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            if self.use_debug_cam:
                # Debug 相机是 1080x720 [cite: 254] (注：论文中是 800x600，你的代码是 720p)
                self.video_writer = cv2.VideoWriter(video_path, fourcc, 1/FIXED_DELTA_SECONDS, (DEBUG_IMG_DIM_X, DEBUG_IMG_DIM_Y))
            else:
                # 训练相机是拼接后的 (IMG_DIM_X*2, IMG_DIM_Y)
                # self.video_writer = cv2.VideoWriter(video_path, fourcc, 20.0, (IMG_DIM_X*2, IMG_DIM_Y))
                self.video_writer = cv2.VideoWriter(video_path, fourcc, 1/FIXED_DELTA_SECONDS, (IMG_DIM_X, IMG_DIM_Y))
            print(f"[VIDEO] Saved to: {video_path}")

        self.start_distance = start_transform.location.distance(target_location)
        # 记录过程中的历史最短距离（用于更严苛的判定）
        self.min_distance = self.start_distance

        # 6. 推进模拟器并获取观察值
        self.world.tick()
        obs = self._get_observation()
        info = {}

        return obs, info
    
    def step(self, action):
        # 记录执行动作前的距离
        dist_pre = self.ego.get_location().distance(self.target_location)
        
        # 1. 执行动作 (加速, 转向, 制动)
        self._apply_action(action)
        self.world.tick()

        # 2. 获取新观察值
        obs = self._get_observation()

        if self.is_recording and self.video_writer is not None:
            if self.use_debug_cam:
                try:
                    # 获取 150 FOV 的全景画面 [cite: 254]
                    _, debug_img = self.ego.sensor_data['debug_camera'].get(timeout=1.0)
                    frame = cv2.cvtColor(debug_img, cv2.COLOR_RGB2BGR)
                    self.video_writer.write(frame)
                except:
                    print("Warning: Debug camera frame timeout.")
            else:
                # 获取训练用的拼接画面 (Left + Right) [cite: 167]
                # obs['visual'] 形状为 (4, H, W, 3)，取最后一帧
                frame = obs['visual'][-1].astype(np.uint8)
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                self.video_writer.write(frame_bgr)

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
        reward = self._compute_reward(speed, dist_pre, dist_curr, collided, offroad, otherlane, reached)

        if too_far:
            reward = -50.0  # 惩罚项
            print(f"[FAILED] Ego is moving away from destination. Dist: {dist_curr:.2f}")
        
        # 5. 判定结束 [cite: 256]
        terminated = collided or reached or too_far
        truncated = False # 也可以根据步数设置

        # 在结束时释放资源
        if (terminated or truncated) and self.is_recording:
            self.stop_recording()
        
        return obs, reward, terminated, truncated, {}
    
    def stop_recording(self):
        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None
            self.is_recording = False
            print("[DEBUG] Video released manually.")

    def close(self):
        self.ego.destroy()
        settings = self.world.get_settings()
        settings.synchronous_mode = False
        self.world.apply_settings(settings)

    '''def _apply_action(self, action):
        # 如果 action 是 Tensor，先转到 cpu 并转为 numpy
        if torch.is_tensor(action):
            action = action.detach().cpu().numpy().flatten()
        
        # 现在可以安全地转为 float 了
        steer = float(action[0])
        if float(action[1]) > 0.1:
            throttle = float(action[1])
            brake = 0
        elif float(action[1]) < -0.1:
            throttle = 0
            brake = -float(action[1])
        else:
            throttle = 0
            brake = 0
        
        self.ego.apply_control(throttle=throttle, steer=steer, brake=brake)'''
    
    def _apply_action(self, action):
        if torch.is_tensor(action):
            action = action.detach().cpu().numpy().flatten()
        
        steer = float(action[0])    # 转向 [-1, 1]
        throttle = float(action[1]) # 加速 [0, 1]
        brake = float(action[2])    # 刹车 [0, 1]
        
        self.ego.apply_control(throttle=throttle, steer=steer, brake=brake)

