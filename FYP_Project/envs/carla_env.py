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
    def __init__(self, town, max_retries = 3):
        super().__init__()
        self.town = town
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
        self.world = self.client.load_world(self.town, map_layers=carla.MapLayer.NONE)
        env_objs = self.world.get_environment_objects(carla.CityObjectLabel.Buildings)
        target_ids = set()
        for obj in env_objs:
            if "Building_Name_In_Editor" in obj.name: 
                target_ids.add(obj.id)

        if target_ids:
            self.world.enable_environment_objects(target_ids, False)

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
        # 1. Add retry mechanism to prevent the queue from being temporarily empty
        # img_l, img_r = None, None
        img_l, img_r, img_f = None, None, None
        retry_count = 0
        while img_l is None or img_r is None or img_f is None and retry_count < 5:
            try:
                # 1. Get the data from three viewpoints
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
        
        # 3. Vectorized calculation
        # Direct calculation of the relative vector
        d_vec = np.array([self.target_location.x - loc.x, 
                        self.target_location.y - loc.y], dtype=np.float32)
        
        # Rotation calculation (using pre-computed sin/cos is faster)
        rad = math.radians(-trans.rotation.yaw)
        c, s = math.cos(rad), math.sin(rad)
        
        # Shorthand for rotation matrix
        lx = d_vec[0] * c - d_vec[1] * s
        ly = d_vec[0] * s + d_vec[1] * c
        
        # 4. Normalization
        norm = math.sqrt(lx**2 + ly**2) + 1e-6
        goal_vec = np.array([lx/norm, ly/norm], dtype=np.float32)
        
        return combined_img, goal_vec, img_debug
    
    def _spawn_at_junction(self, end=True):
        # Only attempt to spawn vehicles at spots marked as "start"
        if not end:
            spoint = [p for p in self.current_junction_data if p.get('start')]
        else:
            spoint = self.current_junction_data

        for pt in spoint:
            tf = carla.Transform(carla.Location(x=pt['x'], y=pt['y'], z=pt['z']), 
                                carla.Rotation(yaw=pt['rotate']))
            blueprint = np.random.choice(self.blueprints)
            # try_spawn_actor will automatically handle collision detection, returning None if the position is occupied
            vehicle = self.world.try_spawn_actor(blueprint, tf)
            if vehicle is not None:
                self._configure_npc_behavior(vehicle)

    def _configure_npc_behavior(self, vehicle):
        """Extracted configuration function to keep code clean"""
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
        
        # Get the nearest waypoint to the current location
        wp = self.map.get_waypoint(location, lane_type=carla.LaneType.Driving)
        
        # Get waypoint direction and vehicle heading direction
        forward_vector = transform.get_forward_vector()
        wp_forward_vector = wp.transform.get_forward_vector()
        
        # Calculate dot product: determine if running in reverse (corresponding to direction detection in paper) [cite: 198, 222]
        dot_product = forward_vector.x * wp_forward_vector.x + forward_vector.y * wp_forward_vector.y

        # 1. Physical distance calculation
        dist_to_lane_center = location.distance(wp.transform.location)
        lane_half_width = wp.lane_width / 2.0

        # 2. Determine Offroad [cite: 205, 209]
        offroad_flag = dist_to_lane_center > (lane_half_width + 0.5)

        # 3. Determine Otherlane (core improvement)
        # On two-way roads, the lane_id sign of the opposite lane is opposite to the current lane
        # If dot_product < 0, it means running in reverse on the opposite lane [cite: 205, 209]
        if dot_product < 0:
            otherlane_flag = True
        else:
            # If direction is same, check if deviation is too large
            otherlane_flag = False

        # 4. Determine on marking 
        on_marking_flag = False
        if not otherlane_flag:
            if dist_to_lane_center > (lane_half_width * 0.8):
                on_marking_flag = True

        return otherlane_flag, on_marking_flag, offroad_flag
    
    def _compute_reward(self, current_v, dist_pre, dist_curr, collided, offroad, otherlane, onmarking, reached):
        # --- Level 1: Sparse Rewards (Life or Death) ---
        if collided or offroad: return -10.0
        if reached: return 10.0
        
        # --- Level 2: Shaping Rewards (Progress) ---
        r_d = (dist_pre - dist_curr) * 0.5
        
        # --- Level 3: Fine-tuning Rewards (Driving Standards) ---
        if current_v < 0.5:
            r_v = (-0.5 + current_v) * 0.1
        else:
            r_v = min(current_v, 10.0) / 33.0
            
        # r_or = -1.0 if offroad else 0.0
        r_ol = -0.2 if otherlane else 0.0
        r_om = -0.025 if onmarking else 0.0
        
        return r_v + r_d + r_ol + r_om
        # return r_v + r_d + r_ol + r_or

    def reset(self, town, level=0, junction_data=None, video_path=None, start_transform=None, target_location=None):
        self.clear_actor()
        self.current_junction_data = junction_data # Save junction data
        self.current_level = level
        self.target_location = target_location
        self.current_step = 0
        self.start_transform = start_transform

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
        speed = np.sqrt(v.x**2 + v.y**2 + v.z**2) # Convert to m/s
        dist_curr = self.ego.get_location().distance(self.target_location)
        
        self.min_distance = min(self.min_distance, dist_curr)
        collided = self.ego.collision_flag 
        reached = dist_curr < 2.0          # Decision threshold for reaching target
        # too_far = dist_curr > (self.start_distance + 25.0)

        # 4. Calculate Equation 7 reward from paper
        reward = self._compute_reward(speed, dist_pre, dist_curr, collided, offroad, otherlane, on_marking, reached)

        raw_img, goal_vec, debug_img = self._get_observation()

        # 5. Determine termination [cite: 256]
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
            terminate_reason=reason, # Must pass this parameter!
            debug_frame=debug_img
        )

        # Release resources on completion
        if (terminated or truncated) and self.video_path is not None:
            os.makedirs(os.path.dirname(self.video_path), exist_ok=True)
            self.obs_buffer.to_video(self.video_path)

        self.current_step += 1
        return self.obs_buffer.get_current_obs(), reward, terminated, truncated, {"reason": reason, "speed": speed}

    def _apply_action(self, action):
        steer = float(action[0])
        acc = float(action[1])

        if acc >= 0.05:
            throttle = (acc - 0.05) / 0.95
            brake = 0.0
        elif acc < -0.05:
            throttle = 0.0
            brake = (-acc - 0.05) / 0.95
        else:
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
                # Calculate Euclidean distance between two points
                dist = curr_loc.distance(prev_loc)

                # If the displacement is less than 0.1 meters within checking cycle, it is stuck
                if dist < 0.1:
                    vehicle.destroy()
                    # Also delete from dictionary to prevent affecting the next loop
                    del self.npc_location_history[v_id]
                    continue
            
            # Update location record
            self.npc_location_history[v_id] = curr_loc

        # Clean up vehicle records that have disappeared
        self.npc_location_history = {k: v for k, v in self.npc_location_history.items() if k in current_ids}