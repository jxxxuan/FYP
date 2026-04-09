import carla
import time

# 1. 把你记录的所有坐标点写在这里 [x, y, z, yaw, 备注名称]
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

    print(f"开始校验共 {len(POINTS_TO_CHECK)} 个点位...")

    for i, p in enumerate(POINTS_TO_CHECK):
        loc = carla.Location(x=p[0], y=p[1], z=p[2])
        rot = carla.Rotation(yaw=p[3])
        name = p[4]

        # --- 1. 视觉标记 ---
        # 画个大绿球和箭头
        debug.draw_point(loc + carla.Location(z=0.2), size=0.2, color=carla.Color(0, 255, 0), life_time=10000)
        debug.draw_arrow(loc + carla.Location(z=0.5), loc + rot.get_forward_vector()*2, thickness=0.1, color=carla.Color(0, 255, 0), life_time=10000.0)
        debug.draw_string(loc + carla.Location(z=2.0), f"[{i}] {name}", color=carla.Color(255, 255, 0), life_time=10000)

        # --- 2. 视角切换 ---
        # 把视角移到点位上方 12 米，低头俯视 (-60度)
        spec_loc = loc + carla.Location(z=12.0) - rot.get_forward_vector() * 5.0 
        spec_rot = carla.Rotation(pitch=-60, yaw=p[3])
        spectator.set_transform(carla.Transform(spec_loc, spec_rot))

        print(f"正在查看点位 {i}: {name} (坐标: {p[0]}, {p[1]})")

    print("所有点位巡航完毕！")

if __name__ == '__main__':
    auto_verify()