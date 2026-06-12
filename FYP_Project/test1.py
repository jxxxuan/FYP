import carla
import time

# 1. Load map
client = carla.Client("localhost", 2000)
client.load_world("Town03_Opt")
world = client.get_world()
print('Map command sent')

# 2. Key step: set fixed delta seconds first, then enable synchronous mode
settings = world.get_settings()
settings.fixed_delta_seconds = 0.05  # Must set, recommended 0.05 (20FPS)
settings.synchronous_mode = True
world.apply_settings(settings)
print('Fixed delta and sync mode set')

# 3. Warm up the world
for _ in range(20):
    world.tick()
print('World stabilized')

# 4. Finally launch Traffic Manager
try:
    tm = client.get_trafficmanager(8000)
    # Force TM to align with this step size
    tm.set_synchronous_mode(True)
    print('TM Synchronized successfully!')
except Exception as e:
    print(f"TM Error: {e}")

# 5. Test if it can run
world.tick()
print('Final tick success!')