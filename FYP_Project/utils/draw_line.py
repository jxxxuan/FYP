import carla

def draw_grid(world, center_loc, grid_range=500, step=50):
    """
    center_loc: Grid center (carla.Location)
    grid_range: Drawing range (meters)
    step: Grid spacing (meters)
    """
    debug = world.debug
    z = center_loc.z + 0.5  # Slightly elevated to prevent embedding in the ground
    
    # Calculate starting and ending coordinates
    min_x = int(center_loc.x - grid_range)
    max_x = int(center_loc.x + grid_range)
    min_y = int(center_loc.y - grid_range)
    max_y = int(center_loc.y + grid_range)

    # 1. Draw vertical lines (fixed X, varying Y) -> represents X-axis grid
    for x in range(min_x, max_x + 1, step):
        start = carla.Location(x=float(x), y=float(min_y), z=z)
        end = carla.Location(x=float(x), y=float(max_y), z=z)
        # Draw line
        debug.draw_line(start, end, thickness=0.1, color=carla.Color(255, 0, 0, 150), life_time=1000.0)
        # Label X coordinates (labeled near Y=0)
        debug.draw_string(carla.Location(x=float(x), y=center_loc.y, z=z+1.0), 
                          f"X={x}", color=carla.Color(255, 50, 50), life_time=1000.0)

    # 2. Draw horizontal lines (fixed Y, varying X) -> represents Y-axis grid
    for y in range(min_y, max_y + 1, step):
        start = carla.Location(x=float(min_x), y=float(y), z=z)
        end = carla.Location(x=float(max_x), y=float(y), z=z)
        # Draw line
        debug.draw_line(start, end, thickness=0.1, color=carla.Color(0, 255, 0, 150), life_time=1000.0)
        # Label Y coordinates (labeled near X=0)
        debug.draw_string(carla.Location(x=center_loc.x, y=float(y), z=z+1.0), 
                          f"Y={y}", color=carla.Color(50, 255, 50), life_time=1000.0)

def main():
    client = carla.Client('192.168.2.3', 2000)
    client.set_timeout(10.0)
    
    # Automatically retrieve the current map to prevent load_world error
    world = client.load_world('town05') 
    
    # Draw a 1000m x 1000m grid around the origin (0,0,0) with a spacing of 50m
    print("Starting to draw coordinate grid lines...")
    draw_grid(world, carla.Location(0, 0, 0), grid_range=500, step=20)
    print("Drawing completed!")

if __name__ == '__main__':
    main()