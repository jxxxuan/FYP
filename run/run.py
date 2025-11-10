import carla
import random
import time
from dotenv import load_dotenv
import os

load_dotenv()

host = os.getenv("CARLA_HOST")
carla_path = os.getenv("CARLA_API_PATH")
#client = carla.Client('127.0.0.1', 2000)
client = carla.Client(host, 2000)
client.set_timeout(10.0)
world = client.get_world()

# 选择车辆蓝图
bp_lib = world.get_blueprint_library()
vehicle_bp = bp_lib.filter('model3')[0]

# 获取可生成点
spawn_points = world.get_map().get_spawn_points()
start_pose = spawn_points[0]   # 起点
end_pose = spawn_points[-1]    # 终点

for i, sp in enumerate(spawn_points):
    world.debug.draw_string(
        sp.location,
        str(i),
        life_time=60.0,  # 持续显示 60 秒
        color=carla.Color(0, 255, 0)  # 绿色
    )

vehicle = world.spawn_actor(vehicle_bp, start_pose)
vehicle.set_autopilot(True)  # 可以先开自动驾驶测试路径

# 让车开一段
time.sleep(120)

vehicle.destroy()
print("Start:", start_pose)
print("End:", end_pose)
