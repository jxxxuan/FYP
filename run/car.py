import carla
import numpy as np
import queue

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
        cam_bp.set_attribute('image_size_x', '1280')
        cam_bp.set_attribute('image_size_y', '720')
        cam_bp.set_attribute('fov', '90')
        cam_bp.set_attribute('sensor_tick', '0.05')
        cam_transform = carla.Transform(carla.Location(x=1.5, z=2.2),carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0))
        self.sensors['front_camera'] = world.spawn_actor(cam_bp, cam_transform, attach_to=self.vehicle)
        cam_transform = carla.Transform(carla.Location(x=1.5, z=2.2),carla.Rotation(pitch=0.0, yaw=-90, roll=0.0))
        self.sensors['left_camera'] = world.spawn_actor(cam_bp, cam_transform, attach_to=self.vehicle)
        cam_transform = carla.Transform(carla.Location(x=1.5, z=2.2),carla.Rotation(pitch=0.0, yaw=90, roll=0.0))
        self.sensors['right_camera'] = world.spawn_actor(cam_bp, cam_transform, attach_to=self.vehicle)

        # LiDAR
        lidar_bp = self.blueprint_library.find('sensor.lidar.ray_cast')
        lidar_bp.set_attribute('channels', '32')
        lidar_bp.set_attribute('range', '80')
        lidar_bp.set_attribute('rotation_frequency', '10')
        lidar_bp.set_attribute('points_per_second', '500000')
        lidar_transform = carla.Transform(carla.Location(x=0.0, z=2.5))
        self.sensors['lidar'] = world.spawn_actor(lidar_bp, lidar_transform, attach_to=self.vehicle)

        # GNSS + IMU
        self.sensors['gnss'] = world.spawn_actor(
            self.blueprint_library.find('sensor.other.gnss'),
            carla.Transform(carla.Location(x=0.0, z=1.0)),
            attach_to=self.vehicle)
        self.sensors['imu'] = world.spawn_actor(
            self.blueprint_library.find('sensor.other.imu'),
            carla.Transform(carla.Location(x=0.0, z=1.0)),
            attach_to=self.vehicle)

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
            'lidar': queue.Queue(maxsize=1),
            'gnss': queue.Queue(maxsize=1),
            'imu': queue.Queue(maxsize=1)
        }

        self.sensors['front_camera'].listen(self._cam_cb)
        self.sensors['lidar'].listen(self._lidar_cb)
        self.sensors['gnss'].listen(self._gnss_cb)
        self.sensors['imu'].listen(self._imu_cb)
        # self.sensors['collision'].listen(self._handle_collision)
        # self.sensors['lane'].listen(self._handle_lane_invade)

    # --- 回调 ---
    def _cam_cb(self, image):
        frame = image.frame  # 这是CARLA给的每tick唯一帧号
        arr = np.frombuffer(image.raw_data, dtype=np.uint8).reshape((image.height, image.width, 4))[:, :, :3]
        if self.sensor_data['front_camera'].full():
            self.sensor_data['front_camera'].get_nowait()
        self.sensor_data['front_camera'].put_nowait((frame, arr))

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

    # -----------------------
    # 销毁所有 actor
    # -----------------------
    def destroy(self):
        for actor in self.actors:
            actor.destroy()
        print("All actors destroyed.")

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


# 使用示例（放在 main.py）
"""
client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.get_world()

car_instance = Car(world)
# ... run simulation ...
car_instance.destroy()
"""
