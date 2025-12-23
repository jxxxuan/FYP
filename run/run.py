import carla
import random
import time
from dotenv import load_dotenv
import os
from car import EgoVehicle

load_dotenv()

host = os.getenv("CARLA_HOST")
carla_path = os.getenv("CARLA_API_PATH")
client = carla.Client(host, 2000)
client.set_timeout(10.0)
world = client.get_world()

# set synchronous mode
settings = world.get_settings()
settings.synchronous_mode = True
settings.fixed_delta_seconds = 0.05       # 每步 0.05 秒
settings.max_substep_delta_time = 0.05    # 每个物理子步 0.05 秒
settings.max_substeps = 2                 # 总共 0.1 秒 > fixed_delta_seconds
world.apply_settings(settings)
#fixed_delta_seconds <= max_substep_delta_time * max_substeps

# 获取可生成点
spawn_points = world.get_map().get_spawn_points()
start_pose = spawn_points[0]   # 起点
end_pose = spawn_points[-1]    # 终点

# 选择车辆蓝图
ego_vehicle = EgoVehicle(world, start_pose)          # 已生成 vehicle + sensors
ego_vehicle.vehicle.set_autopilot(True)  # 开启自动驾驶

trajectories = [[]]

try:
    while True:
        world.tick()     # 如果是同步模式
        loc = ego_vehicle.get_location()
        trajectories[0].append([loc.x, loc.y, loc.z])

except KeyboardInterrupt:
    print("Exiting...")

finally:
    ego_vehicle.destroy()
