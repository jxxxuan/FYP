import carla
from constants import *
from agents.navigation.global_route_planner import GlobalRoutePlanner

def _connect_to_carla(self):
    self.tm = self.client.get_trafficmanager(8000)
    self.tm.set_synchronous_mode(True)
    
def _load_world(self, town):
    settings = self.world.get_settings()
    settings.synchronous_mode = True
    settings.fixed_delta_seconds = FIXED_DELTA_SECONDS     
    settings.max_substep_delta_time = SUBSTEP_DELTA
    settings.max_substeps = MAX_SUBSTEPS
    self.world.apply_settings(settings)
    self.map = self.world.get_map()
    self.grp = GlobalRoutePlanner(self.map, GRP)

if __name__ == '__main__':
    for i in range(100):
        client = carla.Client(CARLA_HOST, int(CARLA_PORT))
        client.set_timeout(10.0)
        world = client.load_world('town04')

        