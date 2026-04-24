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
        self.world = world
        self.blueprint_library = world.get_blueprint_library()
        self.actors = []  # 存所有 actor，方便销毁
        self.sensors = {}
        self.map_obj = self.world.get_map()

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
        # cam_transform = carla.Transform(carla.Location(x=1.5, z=2.2),carla.Rotation(pitch=-7.5, yaw=0.0, roll=0.0))
        # self.sensors['front_camera'] = world.spawn_actor(cam_bp, cam_transform, attach_to=self.vehicle)
        cam_transform = carla.Transform(carla.Location(x=1.5, z=2.2),carla.Rotation(pitch=-7.5, yaw=-38.5, roll=0.0))
        self.sensors['left_camera'] = world.spawn_actor(cam_bp, cam_transform, attach_to=self.vehicle)
        cam_transform = carla.Transform(carla.Location(x=1.5, z=2.2),carla.Rotation(pitch=-7.5, yaw=38.5, roll=0.0))
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

        # 队列
        self.gnss_queue = queue.Queue()
        self.imu_queue = queue.Queue()

        self.sensor_data = {
            'debug_camera': queue.Queue(maxsize=1),
            # 'front_camera': queue.Queue(maxsize=1),
            'left_camera': queue.Queue(maxsize=1),
            'right_camera': queue.Queue(maxsize=1),
        }

        self.sensors['debug_camera'].listen(lambda img: self._cam_cb('debug_camera', img))
        # self.sensors['front_camera'].listen(lambda img: self._cam_cb('front_camera', img))
        self.sensors['left_camera'].listen(lambda img: self._cam_cb('left_camera', img))
        self.sensors['right_camera'].listen(lambda img: self._cam_cb('right_camera', img))
        self.sensors['collision'].listen(self._handle_collision)

        # 1. [必须添加] 初始化标志位
        self.collision_flag = False
        self.update_flags()

    '''def update_flags(self):
        self.otherlane_flag = False
        self.offroad_flag = False'''
    
    def update_flags(self):
        location = self.vehicle.get_location()
        wp = self.map_obj.get_waypoint(location, lane_type=carla.LaneType.Driving)
        dist_to_lane_center = location.distance(wp.transform.location)
        
        self.offroad_flag = dist_to_lane_center > (wp.lane_width / 2.0 + 0.5)

        self.otherlane_flag = False
    
        v_vec = location - wp.transform.location
        wp_right_vec = wp.transform.get_right_vector()
        
        # 点积 > 0 说明在右侧，点积 < 0 说明在左侧
        dot = v_vec.x * wp_right_vec.x + v_vec.y * wp_right_vec.y

        deviation = dist_to_lane_center / (wp.lane_width / 2.0)
        
        if deviation > 0.8:
            target_marking = wp.right_lane_marking if dot > 0 else wp.left_lane_marking
            
            if target_marking.type == carla.LaneMarkingType.Solid or target_marking.color == carla.LaneMarkingColor.Yellow:
                self.otherlane_flag = True

    def _handle_collision(self, event):
        # 只要发生碰撞，就把标志位置为 True
        self.collision_flag = True

    # 4. [建议添加] 重置标志位的方法，用于每个 Episode 开始时
    def reset_flags(self):
        self.collision_flag = False
        self.offroad_flag = False
        self.otherlane_flag = False

    # --- 回调 ---
    def _cam_cb(self, key, image):
        """通用回调：确保输出 RGB 数组格式对齐 ViT 输入要求 """

        """通用侧向摄像头回调"""
        # 转换为 RGB 数组
        arr = np.frombuffer(image.raw_data, dtype=np.uint8).reshape((image.height, image.width, 4))[:, :, :3]
        
        if self.sensor_data[key].full():
            self.sensor_data[key].get_nowait()
        self.sensor_data[key].put_nowait(arr)

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
        # 先停止所有传感器监听
        for name, sensor in self.sensors.items():
            if sensor is not None and sensor.is_alive:
                sensor.stop()
                
        # 销毁所有 actor
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

