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

        # 生成车辆
        car_bp = self.blueprint_library.filter('model3')[0]
        car_bp.set_attribute('role_name', 'ego')
        self.vehicle = world.spawn_actor(car_bp, spawn_point)  # spawn_point 可以换
        self.actors.append(self.vehicle)

        # 摄像头
        cam_bp = self.blueprint_library.find('sensor.camera.rgb')
        cam_bp.set_attribute('image_size_x', str(IMG_DIM_X))
        cam_bp.set_attribute('image_size_y', str(IMG_DIM_Y))
        cam_bp.set_attribute('fov', '40')
        cam_transform = carla.Transform(carla.Location(x=1.5, z=2),carla.Rotation(pitch=-10, yaw=-40, roll=0.0))
        self.sensors['left_camera'] = world.spawn_actor(cam_bp, cam_transform, attach_to=self.vehicle)
        cam_transform = carla.Transform(carla.Location(x=1.5, z=2),carla.Rotation(pitch=-10, yaw=0, roll=0.0))
        self.sensors['front_camera'] = world.spawn_actor(cam_bp, cam_transform, attach_to=self.vehicle)
        cam_transform = carla.Transform(carla.Location(x=1.5, z=2),carla.Rotation(pitch=-10, yaw=40, roll=0.0))
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
        
        self.actors += list(self.sensors.values())

        self.sensor_data = {
            'debug_camera': queue.Queue(maxsize=1),
            'left_camera': queue.Queue(maxsize=1),
            'front_camera': queue.Queue(maxsize=1),
            'right_camera': queue.Queue(maxsize=1),
        }

        self.sensors['debug_camera'].listen(lambda img: self._cam_cb('debug_camera', img))
        self.sensors['left_camera'].listen(lambda img: self._cam_cb('left_camera', img))
        self.sensors['right_camera'].listen(lambda img: self._cam_cb('right_camera', img))
        self.sensors['front_camera'].listen(lambda img: self._cam_cb('front_camera', img))
        self.sensors['collision'].listen(self._handle_collision)
        
        # 1. [必须添加] 初始化标志位
        self.collision_flag = False

    def _handle_collision(self, event):
        # 只要发生碰撞，就把标志位置为 True
        self.collision_flag = True

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
        for name, sensor in self.sensors.items():
            if sensor is not None and sensor.is_alive:
                sensor.stop()
        # 清空队列
        for key in self.sensor_data:
            while not self.sensor_data[key].empty():
                self.sensor_data[key].get_nowait()
        for actor in self.actors:
            if actor is not None and actor.is_alive:
                actor.destroy()
        self.sensors.clear()
        self.actors.clear()
        
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