import carla
from constants import *
import time


client = carla.Client(CARLA_HOST, int(CARLA_PORT))
client.set_timeout(10.0)
client.load_world("Town03_Opt", carla.MapLayer.Buildings | carla.MapLayer.ParkedVehicles)
print('loaded1')
time.sleep(10)
tm = client.get_trafficmanager()
tm.shut_down()
print('got tm')
tm.set_synchronous_mode(True)
print('loaded2')