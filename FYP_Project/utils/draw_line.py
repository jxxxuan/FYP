import carla

def draw_grid(world, center_loc, grid_range=500, step=50):
    """
    center_loc: 网格中心 (carla.Location)
    grid_range: 绘制范围 (米)
    step: 刻度间距 (米)
    """
    debug = world.debug
    z = center_loc.z + 0.5  # 稍微抬高，防止埋入地下
    
    # 计算起始和结束坐标
    min_x = int(center_loc.x - grid_range)
    max_x = int(center_loc.x + grid_range)
    min_y = int(center_loc.y - grid_range)
    max_y = int(center_loc.y + grid_range)

    # 1. 绘制纵向线 (固定 X, 变化 Y) -> 代表 X 轴刻度
    for x in range(min_x, max_x + 1, step):
        start = carla.Location(x=float(x), y=float(min_y), z=z)
        end = carla.Location(x=float(x), y=float(max_y), z=z)
        # 画线
        debug.draw_line(start, end, thickness=0.1, color=carla.Color(255, 0, 0, 150), life_time=1000.0)
        # 标 X 坐标数 (沿 Y=0 附近标注)
        debug.draw_string(carla.Location(x=float(x), y=center_loc.y, z=z+1.0), 
                          f"X={x}", color=carla.Color(255, 50, 50), life_time=1000.0)

    # 2. 绘制横向线 (固定 Y, 变化 X) -> 代表 Y 轴刻度
    for y in range(min_y, max_y + 1, step):
        start = carla.Location(x=float(min_x), y=float(y), z=z)
        end = carla.Location(x=float(max_x), y=float(y), z=z)
        # 画线
        debug.draw_line(start, end, thickness=0.1, color=carla.Color(0, 255, 0, 150), life_time=1000.0)
        # 标 Y 坐标数 (沿 X=0 附近标注)
        debug.draw_string(carla.Location(x=center_loc.x, y=float(y), z=z+1.0), 
                          f"Y={y}", color=carla.Color(50, 255, 50), life_time=1000.0)

def main():
    client = carla.Client('192.168.2.3', 2000)
    client.set_timeout(10.0)
    
    # 自动获取当前地图，避免 load_world 报错
    world = client.load_world('town05') 
    
    # 在原点 (0,0,0) 周围画一个 1000米x1000米 的网格，每 50米 一个刻度
    print("开始绘制坐标刻度线...")
    draw_grid(world, carla.Location(0, 0, 0), grid_range=500, step=20)
    print("绘制完成！")

if __name__ == '__main__':
    main()