import carla
import time

# 1. Put all coordinates you recorded here [x, y, z, yaw, note_name]
POINTS_TO_CHECK = [
    [80, 5, 0.5, 0.0, "Task1.1"],
    [80, 2, 0.5, 90.0, "Task1.2"],
    [80, -2, 0.5, 180.0, "Task1.3"],
    [80, -5, 0.5, 270.0, "Task1.4"],
]

def auto_verify():
    client = carla.Client('192.168.2.3', 2000)
    client.set_timeout(10.0)
    world = client.load_world('town03')
    debug = world.debug
    spectator = world.get_spectator()

    print(f"Starting verification of {len(POINTS_TO_CHECK)} locations...")

    for i, p in enumerate(POINTS_TO_CHECK):
        loc = carla.Location(x=p[0], y=p[1], z=p[2])
        rot = carla.Rotation(yaw=p[3])
        name = p[4]

        # --- 1. Visual Markers ---
        # Draw a large green sphere and arrow
        debug.draw_point(loc + carla.Location(z=0.2), size=0.2, color=carla.Color(0, 255, 0), life_time=10000)
        debug.draw_arrow(loc + carla.Location(z=0.5), loc + rot.get_forward_vector()*2, thickness=0.1, color=carla.Color(0, 255, 0), life_time=10000.0)
        debug.draw_string(loc + carla.Location(z=2.0), f"[{i}] {name}", color=carla.Color(255, 255, 0), life_time=10000)

        # --- 2. Camera View Switch ---
        # Move the camera view 12 meters above the location, tilt down (-60 degrees)
        spec_loc = loc + carla.Location(z=12.0) - rot.get_forward_vector() * 5.0 
        spec_rot = carla.Rotation(pitch=-60, yaw=p[3])
        spectator.set_transform(carla.Transform(spec_loc, spec_rot))

        print(f"Viewing location {i}: {name} (Coordinates: {p[0]}, {p[1]})")

    print("All locations navigated!")

if __name__ == '__main__':
    auto_verify()