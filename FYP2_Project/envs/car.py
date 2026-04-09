import carla
import numpy as np
import queue
import cv2
from dotenv import load_dotenv
import os
from constants import IMG_DIM
load_dotenv()

class EgoVehicle:
    def __init__(self, world, spawn_point):
        self.world = world
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
        cam_bp.set_attribute('image_size_x', str(IMG_DIM))
        cam_bp.set_attribute('image_size_y', str(IMG_DIM))
        cam_bp.set_attribute('fov', '50')
        cam_transform = carla.Transform(carla.Location(x=1.5, z=2.2),carla.Rotation(pitch=-10.0, yaw=0.0, roll=0.0))
        self.sensors['front_camera'] = world.spawn_actor(cam_bp, cam_transform, attach_to=self.vehicle)
        cam_transform = carla.Transform(carla.Location(x=1.5, z=2.2),carla.Rotation(pitch=-10.0, yaw=-60, roll=0.0))
        self.sensors['left_camera'] = world.spawn_actor(cam_bp, cam_transform, attach_to=self.vehicle)
        cam_transform = carla.Transform(carla.Location(x=1.5, z=2.2),carla.Rotation(pitch=-10.0, yaw=60, roll=0.0))
        self.sensors['right_camera'] = world.spawn_actor(cam_bp, cam_transform, attach_to=self.vehicle)

        # Collision + Lane invasion
        self.sensors['collision'] = world.spawn_actor(
            self.blueprint_library.find('sensor.other.collision'),
            carla.Transform(), attach_to=self.vehicle)
        self.sensors['lane'] = world.spawn_actor(
            self.blueprint_library.find('sensor.other.lane_invasion'),
            carla.Transform(), attach_to=self.vehicle)
        
        self.actors += list(self.sensors.values())

        # 队列
        self.gnss_queue = queue.Queue()
        self.imu_queue = queue.Queue()

        self.sensor_data = {
            'front_camera': queue.Queue(maxsize=1),
            'left_camera': queue.Queue(maxsize=1),
            'right_camera': queue.Queue(maxsize=1),
        }

        self.sensors['front_camera'].listen(lambda img: self._cam_cb('front_camera', img))
        self.sensors['left_camera'].listen(lambda img: self._cam_cb('left_camera', img))
        self.sensors['right_camera'].listen(lambda img: self._cam_cb('right_camera', img))
        self.sensors['collision'].listen(self._handle_collision)
        self.sensors['lane'].listen(self._handle_lane_invade)

        # 1. [必须添加] 初始化标志位
        self.collision_flag = False
        self.offroad_flag = False  # 对应车道线惩罚
        self.otherlane_flag = False

    # 3. [必须添加] 编写回调函数来修改标志位
    def _handle_collision(self, event):
        # 只要发生碰撞，就把标志位置为 True
        self.collision_flag = True

    def _handle_lane_invade(self, event):
        # 获取交叉的线类型
        for marking in event.crossed_lane_markings:
            # 如果是路边缘线（通常是 Broken/Solid White/Yellow，取决于地图定义）
            # 或者进入了非授权区域
            if marking.type == carla.LaneMarkingType.Other:
                self.offroad_flag = True
            else:
                # 只要跨过了任何线（实线、双黄线等），通常在训练中视为进入 other lane
                self.otherlane_flag = True

    # 4. [建议添加] 重置标志位的方法，用于每个 Episode 开始时
    def reset_flags(self):
        self.collision_flag = False
        self.offroad_flag = False
        self.otherlane_flag = False

    # --- 回调 ---

    def _cam_cb(self, key, image):
        """通用侧向摄像头回调"""
        frame = image.frame
        # 转换为 RGB 数组
        arr = np.frombuffer(image.raw_data, dtype=np.uint8).reshape((image.height, image.width, 4))[:, :, :3]
        
        if self.sensor_data[key].full():
            self.sensor_data[key].get_nowait()
        self.sensor_data[key].put_nowait((frame, arr))

    def _lidar_cb(self, point_cloud):
        points = np.frombuffer(point_cloud.raw_data, dtype=np.float32).reshape(-1, 4)
        if self.sensor_data['lidar'].full():
            self.sensor_data['lidar'].get_nowait()
        self.sensor_data['lidar'].put_nowait(points)

    def _gnss_cb(self, g):
        pos = (g.latitude, g.longitude, g.altitude)
        if self.sensor_data['gnss'].full():
            self.sensor_data['gnss'].get_nowait()
        self.sensor_data['gnss'].put_nowait(pos)

    def _imu_cb(self, i):
        acc = np.array(i.accelerometer)
        if self.sensor_data['imu'].full():
            self.sensor_data['imu'].get_nowait()
        self.sensor_data['imu'].put_nowait(acc)

    def destroy(self):
        # 停止所有监听，防止销毁过程中回调函数报错
        for sensor in self.sensors.values():
            sensor.stop()
        if hasattr(self, 'debug_camera'):
            self.debug_camera.stop()
            
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
        # 如果找不到这个属性，就去 self.vehicle 里面找
        return getattr(self.vehicle, name)

