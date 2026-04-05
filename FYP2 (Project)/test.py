from utils.CarlaPainter.carla_painter import CarlaPainter
import time

painter = CarlaPainter('localhost', 8081)

# 只传一条最简单的线
simple_line = [[[0, 0, 5], [10, 10, 5]]] 

try:
    while True:
        # 强制只传线，不传点，排除干扰
        painter.draw_polylines(simple_line)
        print("Sent simple line")
        time.sleep(1)
except Exception as e:
    print(e)