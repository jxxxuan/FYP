import carla
import random
import time
from dotenv import load_dotenv
import os
from envs.car import EgoVehicle

load_dotenv()

host = os.getenv("CARLA_HOST")
carla_path = os.getenv("CARLA_API_PATH")
client = carla.Client(host, 2000)
client.set_timeout(10.0)
world = client.get_world()

# set synchronous mode
settings = world.get_settings()
settings.synchronous_mode = False
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
        # 在异步模式下，使用 wait_for_tick() 等待服务器更新一帧
        # 这样你的循环速度会和服务器渲染速度保持一致，不会过度占用 CPU
        world_snapshot = world.wait_for_tick()
        
        loc = ego_vehicle.get_location()
        trajectories[0].append([loc.x, loc.y, loc.z])
        
        # 打印一下，确认程序在跑
        print(f"Vehicle at: {loc.x}, {loc.y}")

except KeyboardInterrupt:
    print("Exiting...")

finally:
    # 记得把设置改回去，或者在退出时清理
    settings.synchronous_mode = False
    world.apply_settings(settings)
    ego_vehicle.destroy()
