import carla
from constants import *

client = carla.Client(CARLA_HOST, int(CARLA_PORT))
client.set_timeout(10.0)
client.load_world("Town03_Opt")