import carla
import numpy as np
import queue
import cv2
from dotenv import load_dotenv
import os
from constants import DEBUG_IMG_DIM_X, DEBUG_IMG_DIM_Y
from hyperparameter import IMG_DIM_X, IMG_DIM_Y
load_dotenv()

class EgoVehicle:
    def __init__(self, world, spawn_point):
        self.blueprint_library = world.get_blueprint_library()
        self.actors = []  # 存所有 actor，方便销毁
        self.sensors = {}
        self.map_obj = world.get_map()

        # 生成车辆
        car_bp = self.blueprint_library.filter('model3')[0]
        car_bp.set_attribute('role_name', 'ego')
        self.vehicle = world.spawn_actor(car_bp, spawn_point)  # spawn_point 可以换
        self.actors.append(self.vehicle)

        # 摄像头
        cam_bp = self.blueprint_library.find('sensor.camera.rgb')
        cam_bp.set_attribute('image_size_x', str(IMG_DIM_X))
        cam_bp.set_attribute('image_size_y', str(IMG_DIM_Y))
        cam_bp.set_attribute('fov', '80')
        cam_transform = carla.Transform(carla.Location(x=1.5, z=2.2),carla.Rotation(pitch=-7.5, yaw=-39.5, roll=0.0))
        # cam_transform = carla.Transform(carla.Location(x=1.5, z=2.2),carla.Rotation(pitch=-7.5, yaw=-38.5, roll=0.0))
        self.sensors['left_camera'] = world.spawn_actor(cam_bp, cam_transform, attach_to=self.vehicle)
        cam_transform = carla.Transform(carla.Location(x=1.5, z=2.2),carla.Rotation(pitch=-7.5, yaw=39.5, roll=0.0))
        # cam_transform = carla.Transform(carla.Location(x=1.5, z=2.2),carla.Rotation(pitch=-7.5, yaw=38.5, roll=0.0))
        self.sensors['right_camera'] = world.spawn_actor(cam_bp, cam_transform, attach_to=self.vehicle)

        cam_bp = self.blueprint_library.find('sensor.camera.rgb')
        cam_bp.set_attribute('image_size_x', str(DEBUG_IMG_DIM_X))
        cam_bp.set_attribute('image_size_y', str(DEBUG_IMG_DIM_Y))
        cam_bp.set_attribute('fov', '150')
        cam_transform = carla.Transform(carla.Location(x=1.5, z=2.2),carla.Rotation(pitch=-10.0, yaw=0.0, roll=0.0))
        self.sensors['debug_camera'] = world.spawn_actor(cam_bp, cam_transform, attach_to=self.vehicle)

        # Collision + Lane invasion
        self.sensors['collision'] = world.spawn_actor(
            self.blueprint_library.find('sensor.other.collision'),
            carla.Transform(), attach_to=self.vehicle)
        self.sensors['lane'] = world.spawn_actor(
            self.blueprint_library.find('sensor.other.lane_invasion'),
            carla.Transform(), attach_to=self.vehicle)
        
        self.actors += list(self.sensors.values())

        self.sensor_data = {
            'debug_camera': queue.Queue(maxsize=1),
            'left_camera': queue.Queue(maxsize=1),
            'right_camera': queue.Queue(maxsize=1),
        }

        self.sensors['debug_camera'].listen(lambda img: self._cam_cb('debug_camera', img))
        self.sensors['left_camera'].listen(lambda img: self._cam_cb('left_camera', img))
        self.sensors['right_camera'].listen(lambda img: self._cam_cb('right_camera', img))
        self.sensors['collision'].listen(self._handle_collision)

        # 1. [必须添加] 初始化标志位
        self.reset_flags()

    def teleport(self, transform):
        """复用车辆的关键：将其瞬移到新起点，并重置物理状态"""
        self.vehicle.set_transform(transform)
        # 必须重置速度和角速度，否则车会带着上一局的动量飞出去
        self.vehicle.set_target_velocity(carla.Vector3D(0, 0, 0))
        self.vehicle.set_target_angular_velocity(carla.Vector3D(0, 0, 0))
        for q in self.sensor_data.values():
            while not q.empty():
                try:
                    q.get_nowait()
                except:
                    break
        self.reset_flags()
    
    def update_flags(self):
        location = self.vehicle.get_location()
        velocity = self.vehicle.get_velocity()
        transform = self.vehicle.get_transform()
        # 减少重复 API 调用
        wp = self.map_obj.get_waypoint(location, lane_type=carla.LaneType.Driving)
        
        # 物理距离计算
        dist_to_lane_center = location.distance(wp.transform.location)
        lane_half_width = wp.lane_width / 2.0

        forward_vector = transform.get_forward_vector()
        wp_forward_vector = wp.transform.get_forward_vector()

        dot_product = forward_vector.x * wp_forward_vector.x + forward_vector.y * wp_forward_vector.y
        
        # 预重置 Flag
        self.offroad_flag = dist_to_lane_center > (lane_half_width + 0.5)
        v_vec_x = location.x - wp.transform.location.x
        v_vec_y = location.y - wp.transform.location.y
        wp_right = wp.transform.get_right_vector()
        # 计算相对于车道中心的横向偏移量（带方向）
        lateral_dist = v_vec_x * wp_right.x + v_vec_y * wp_right.y

        # 只有当中心点偏离方向与对向车道一致，且偏离距离超过车道宽度的一半时才判定
        if dot_product < 0 and abs(lateral_dist) > lane_half_width:
            self.otherlane_flag = True
        else:
            self.otherlane_flag = False

        self.on_marking_flag = False
        if not self.otherlane_flag:
            if dist_to_lane_center > (lane_half_width * 0.8):
                self.on_marking_flag = True

    def _handle_collision(self, event):
        # 只要发生碰撞，就把标志位置为 True
        self.collision_flag = True

    # 4. [建议添加] 重置标志位的方法，用于每个 Episode 开始时
    def reset_flags(self):
        self.collision_flag = False
        self.offroad_flag = False
        self.otherlane_flag = False
        self.on_marking_flag = False

    # --- 回调 ---
    def _cam_cb(self, key, image):
        """通用回调：确保输出 RGB 数组格式对齐 ViT 输入要求 """

        """通用侧向摄像头回调"""
        # 转换为 RGB 数组
        arr = np.frombuffer(image.raw_data, dtype=np.uint8).reshape((image.height, image.width, 4))[:, :, :3]
        
        if self.sensor_data[key].full():
            self.sensor_data[key].get_nowait()
        self.sensor_data[key].put_nowait(arr)

    def destroy(self):
        # 1. 先断开所有回调连接
        for name, sensor in self.sensors.items():
            if sensor is not None and sensor.is_alive:
                sensor.stop()
        
        # 3. 销毁 Actor
        for actor in self.actors:
            if actor is not None and actor.is_alive:
                actor.destroy()
        
    def apply_control(self, throttle=0.0, steer=0.0, brake=0.0):
        """
        throttle: 0~1
        steer: -1~1
        brake: 0~1
        """
        control = carla.VehicleControl()
        control.throttle = float(np.clip(throttle, 0.0, 1.0))
        control.steer = float(np.clip(steer, -1.0, 1.0))
        control.brake = float(np.clip(brake, 0.0, 1.0))
        self.vehicle.apply_control(control)

    def __getattr__(self, name):
        if self.vehicle is not None:
            return getattr(self.vehicle, name)
        raise AttributeError(f"'EgoVehicle' has no attribute '{name}'")