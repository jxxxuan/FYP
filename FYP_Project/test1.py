import carla
from constants import *
import time

# 1. 加载地图
client = carla.Client(CARLA_HOST, int(CARLA_PORT))
client.set_timeout(10.0)
client.load_world("Town03_Opt")
world = client.get_world()
print('Map command sent')

time.sleep(5) 

# 3. 开启世界同步，但不开启 TM 同步
settings = world.get_settings()
settings.synchronous_mode = True
world.apply_settings(settings)

# 4. 手动 Tick 几次，让物理引擎和地图数据对齐
for _ in range(20):
    world.tick()
print('World stabilized')

# 5. 最后再启动 TM
tm = client.get_trafficmanager(8000)
tm.set_synchronous_mode(True)
print('TM successfully joined!')