import carla
from agents.navigation.global_route_planner import GlobalRoutePlanner
from constants import CARLA_HOST

client = carla.Client(CARLA_HOST, 2000)
client.set_timeout(10.0)
world = client.get_world()
wmap = world.get_map()

grp = GlobalRoutePlanner(wmap, 2.0)
origin = carla.Location(x=230, y=195, z=0)
destination = carla.Location(x=50, y=200, z=0)

route = grp.trace_route(origin, destination)
for wp, option in route:
    loc = wp.transform.location
    world.debug.draw_point(loc, size=0.1, color=carla.Color(255,0,0), life_time=0)

