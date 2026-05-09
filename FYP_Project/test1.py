import carla
import time

# 1. 加载地图
client = carla.Client("localhost", 2000)
client.load_world("Town03_Opt")
world = client.get_world()
print('Map command sent')

# 2. 关键：先设置固定步长，再开启同步模式
settings = world.get_settings()
settings.fixed_delta_seconds = 0.05  # 必须设置，建议 0.05 (20FPS)
settings.synchronous_mode = True
world.apply_settings(settings)
print('Fixed delta and sync mode set')

# 3. 预热世界
for _ in range(20):
    world.tick()
print('World stabilized')

# 4. 最后拉起 TM
try:
    tm = client.get_trafficmanager(8000)
    # 强制 TM 也要对齐这个步长
    tm.set_synchronous_mode(True)
    print('TM Synchronized successfully!')
except Exception as e:
    print(f"TM Error: {e}")

# 5. 测试一下能不能跑
world.tick()
print('Final tick success!')