import carla
from constants import *

client = carla.Client(CARLA_HOST, int(CARLA_PORT))
client.set_timeout(10.0)
# tm = client.get_trafficmanager(8000)
# tm.set_synchronous_mode(True)
client.load_world("Town03_Opt")
print('loaded1')
tm = client.get_trafficmanager(8000)
print('got tm')
tm.set_synchronous_mode(True)
print('loaded2')