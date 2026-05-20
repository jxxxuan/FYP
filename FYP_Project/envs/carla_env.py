import math
import gymnasium as gym
from gymnasium import spaces
import numpy as np
import carla
from envs.car import EgoVehicle
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
        self._connect_to_carla()
        self.obs_buffer = ObsBuffer(stack=4)
        self.current_town = None
        self.max_retries = max_retries
        self.blueprints = [bp for bp in self.world.get_blueprint_library().filter('vehicle.*') 
                    if bp.get_attribute('base_type').as_str().lower() != 'bicycle']
        self.npc_location_history = {}

    def _connect_to_carla(self):
        self.client = carla.Client(CARLA_HOST, int(CARLA_PORT))
        self.client.set_timeout(30.0)
        self.tm = self.client.get_trafficmanager(8000)
        self.tm.set_synchronous_mode(True)
        self.world = self.client.get_world()
    
    def _load_world(self, town="town03"):
        self.clear_actor()
        # target_town = town if town.lower().endswith("_Opt") else f"{town}_Opt"
        target_town = town
        if self.current_town == None or not target_town.lower() == self.current_town.lower():
            self.clear_world()
            try:
                self.world = self.client.load_world(target_town,map_layers=carla.MapLayer.NONE)
                env_objs = self.world.get_environment_objects(carla.CityObjectLabel.Buildings)
                target_ids = set()
                for obj in env_objs:
                    if "Building_Name_In_Editor" in obj.name: 
                        target_ids.add(obj.id)

                if target_ids:
                    self.world.enable_environment_objects(target_ids, False)
            except RuntimeError as e:
                raise e
            
        self.current_town = target_town
        settings = self.world.get_settings()
        settings.synchronous_mode = True
        settings.fixed_delta_seconds = FIXED_DELTA_SECONDS     
        settings.max_substep_delta_time = SUBSTEP_DELTA
        settings.max_substeps = MAX_SUBSTEPS
        self.world.apply_settings(settings)
        self.map = self.world.get_map()
        
    def set_ego_autopilot(self):
        grp = GlobalRoutePlanner(self.map, GRP)
        self.route = grp.trace_route(self.start_transform.location, self.target_location)
        self.tm.vehicle_percentage_speed_difference(self.ego.vehicle, 30.0)
        path = [wp[0].transform.location for wp in self.route]
        self.tm.set_path(self.ego.vehicle, path)
        self.tm.distance_to_leading_vehicle(self.ego.vehicle, 4.5)
        self.ego.vehicle.set_autopilot(True, 8000)

    def _get_observation(self):
        # 1. 增加重试机制，防止队列暂时为空
        # img_l, img_r = None, None
        img_l, img_r, img_f = None, None, None
        retry_count = 0
        while img_l is None or img_r is None or img_f is None and retry_count < 5:
            try:
                # 1. 获取三个视角的数据
                img_l = self.ego.sensor_data['left_camera'].get(timeout=2.0)
                img_r = self.ego.sensor_data['right_camera'].get(timeout=2.0)
                img_f = self.ego.sensor_data['front_camera'].get(timeout=2.0)
            except:
                print(f"Warning: Camera queue empty, retrying {retry_count+1}/5...")
                retry_count += 1

        combined_img = np.concatenate([img_l,img_f, img_r], axis=1)

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

    def _configure_npc_behavior(self, vehicle):
        """提取出来的配置函数，保持代码整洁"""
        vehicle.set_autopilot(True, 8000)
        
        speed_min =  30.0 - (self.current_level * 40.0)
        self.tm.vehicle_percentage_speed_difference(vehicle, np.random.uniform(speed_min, speed_min + 20))
        self.tm.distance_to_leading_vehicle(vehicle, max(0.5, 3.0 - (self.current_level * 2.5)))
        lc_prob = self.current_level * 80.0
        self.tm.random_left_lanechange_percentage(vehicle, lc_prob)
        self.tm.random_right_lanechange_percentage(vehicle, lc_prob)
        offset = self.current_level * 0.8
        self.tm.vehicle_lane_offset(vehicle, np.random.uniform(-offset, offset))

    def _lane_detect(self):
        location = self.ego.vehicle.get_location()
        transform = self.ego.vehicle.get_transform()
        
        # 获取当前所在位置最接近的路点
        wp = self.map.get_waypoint(location, lane_type=carla.LaneType.Driving)
        
        # 获取路点方向和车辆前进方向
        forward_vector = transform.get_forward_vector()
        wp_forward_vector = wp.transform.get_forward_vector()
        
        # 计算点乘：判定是否逆行 (对应论文中的方向判定) [cite: 198, 222]
        dot_product = forward_vector.x * wp_forward_vector.x + forward_vector.y * wp_forward_vector.y

        # 1. 物理距离计算
        dist_to_lane_center = location.distance(wp.transform.location)
        lane_half_width = wp.lane_width / 2.0

        # 2. 判定 Offroad [cite: 205, 209]
        offroad_flag = dist_to_lane_center > (lane_half_width + 0.5)

        # 3. 判定 Otherlane (核心改进)
        # 在双向路上，对向车道的 lane_id 符号与本车道相反
        # 只要 dot_product < 0，说明已经在对向车道逆行了 [cite: 205, 209]
        if dot_product < 0:
            otherlane_flag = True
        else:
            # 如果方向相同，再看是否偏离过大
            otherlane_flag = False

        # 4. 判定压线 
        on_marking_flag = False
        if not otherlane_flag:
            if dist_to_lane_center > (lane_half_width * 0.8):
                on_marking_flag = True

        return otherlane_flag, on_marking_flag, offroad_flag
    
    def _compute_reward(self, current_v, dist_pre, dist_curr, collided, offroad, otherlane, onmarking, reached):
        # --- 第一层：生死奖励 (Sparse Rewards) ---
        # 这里的惩罚需要比在原地等待500步的总和来的多吗
        if collided or offroad: return -10.0
        if reached: return 10.0
        
        # --- 第二层：进度奖励 (Shaping Rewards) ---
        # progress_gain = (dist_pre - dist_curr) / max(self.start_distance, 1.0)
        # r_d = progress_gain * 10.0  # 跑完全程正好得 100 分，每一米的分值是平均的
        r_d = (dist_pre - dist_curr) * 0.3
        
        # --- 第三层：驾驶规范 (Fine-tuning Rewards) ---
        if current_v < 0.4:
            r_v = (-0.4 + current_v) * 0.1
        else:
            r_v = min(current_v, 10.0) / 33.0
            
        # r_or = -1.0 if offroad else 0.0
        r_ol = -0.2 if otherlane else 0.0
        r_om = -0.025 if onmarking else 0.0
        
        return r_v + r_d + r_ol + r_om
        # return r_v + r_d + r_ol + r_or

    def reset(self, town, level=0, junction_data=None, video_path=None, start_transform=None, target_location=None):
        self._load_world(town)
        self.current_junction_data = junction_data # 保存路口数据
        self.current_level = level
        self.target_location = target_location
        self.current_step = 0
        self.start_transform = start_transform
        self.total_speed = 0

        try:
            self.ego = EgoVehicle(self.world, self.start_transform)
        except RuntimeError as e:
            self.clear_actor()
            self.ego = EgoVehicle(self.world, self.start_transform)

        self._spawn_at_junction()

        self.last_waypoint_index = 0

        self.start_distance = self.start_transform.location.distance(target_location)
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

        otherlane, on_marking, offroad = self._lane_detect()
        self._apply_action(action)
        self.world.tick()

        v = self.ego.get_velocity()
        speed = np.sqrt(v.x**2 + v.y**2 + v.z**2) # 转为 m/s
        self.total_speed += speed
        dist_curr = self.ego.get_location().distance(self.target_location)
        
        self.min_distance = min(self.min_distance, dist_curr)
        collided = self.ego.collision_flag 
        reached = dist_curr < 2.0          # 到达目标的判定阈值
        # too_far = dist_curr > (self.start_distance + 25.0)

        # 4. 计算论文 Equation 7 的奖励
        reward = self._compute_reward(speed, dist_pre, dist_curr, collided, offroad, otherlane, on_marking, reached)

        raw_img, goal_vec, debug_img = self._get_observation()

        # 5. 判定结束 [cite: 256]
        terminated = collided or offroad or reached
        # terminated = collided or reached
        truncated = self.current_step >= MAX_STEPS - 1

        reason = None
        if terminated or truncated:
            if reached: reason = "R"
            elif collided: reason = "C"
            elif offroad: reason = "O"
            elif truncated: reason = "T"

        if self.current_step % 50 == 0:
            self._spawn_at_junction(end=False)
        if self.current_step % 75 == 0:
            self._clear_stuck_npcs()

        self.obs_buffer.add(
            visual=raw_img, 
            goal=goal_vec, 
            action=action, 
            reward=reward, 
            speed=speed,
            terminate_reason=reason, # 必须传入这个参数！
            debug_frame=debug_img
        )

        # 在结束时释放资源
        if (terminated or truncated) and self.video_path is not None:
            os.makedirs(os.path.dirname(self.video_path), exist_ok=True)
            self.obs_buffer.to_video(self.video_path)

        self.current_step += 1
        return self.obs_buffer.get_current_obs(), reward, terminated, truncated, {"reason": reason, "total speed": (self.total_speed)}

    def _apply_action(self, action):
        # 如果 action 是 Tensor，先转到 cpu 并转为 numpy
        # 现在可以安全地转为 float 了
        steer = float(action[0])
        acc = float(action[1])

        if acc > 0.05:
            # 将 [0.05, 1.0] 映射到 [0.0, 1.0] 的油门
            throttle = (acc - 0.05) / 0.95
            brake = 0.0
        elif acc < -0.05:
            throttle = 0.0
            # 将 [-1.0, -0.05] 映射到 [0.0, 1.0]
            brake = (-acc - 0.05) / 0.95
        else:
            # 在 [-0.05, 0.05] 之间时，车辆处于纯惯性滑行/怠速状态
            throttle = 0.0
            brake = 0.0
        
        self.ego.apply_control(throttle=throttle, steer=steer, brake=brake)

    def close(self):
        self.clear_actor()
        self.clear_world()
        self.shut_down_tm()

    def shut_down_tm(self):
        if hasattr(self, 'tm') and self.tm is not None:
            self.tm.set_synchronous_mode(False)
            self.tm.shut_down()

    def clear_actor(self):
        if hasattr(self, 'ego') and self.ego is not None:
            self.ego.destroy()
            self.ego = None
        actors = list(self.world.get_actors().filter('vehicle.*'))
        actors += list(self.world.get_actors().filter('sensor.*'))
        
        batch = [carla.command.DestroyActor(a) for a in actors]
        
        if batch:
            self.client.apply_batch_sync(batch, True)

    def clear_world(self):
        if hasattr(self, 'world') and self.world is not None:
            settings = self.world.get_settings()
            settings.synchronous_mode = False
            self.world.apply_settings(settings)

    def _clear_stuck_npcs(self):
        all_vehicles = self.world.get_actors().filter('vehicle.*')
        current_ids = []

        for vehicle in all_vehicles:
            v_id = vehicle.id
            if v_id == self.ego.vehicle.id:
                continue
            
            current_ids.append(v_id)
            curr_loc = vehicle.get_location()

            if v_id in self.npc_location_history:
                prev_loc = self.npc_location_history[v_id]
                # 计算两点之间的欧几里得距离
                dist = curr_loc.distance(prev_loc)

                # 如果在检查周期内位移小于 0.5 米，说明卡住了
                if dist < 0.1:
                    vehicle.destroy()
                    # 顺手在字典里也删掉，防止影响下一次循环
                    del self.npc_location_history[v_id]
                    continue
            
            # 更新位置记录
            self.npc_location_history[v_id] = curr_loc

        # 清理已经消失的车辆记录
        self.npc_location_history = {k: v for k, v in self.npc_location_history.items() if k in current_ids}