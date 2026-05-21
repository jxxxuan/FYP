import json
import math
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from constants import TRAIN_JSON, TEST_JSON, INTESECTION_JSON

def get_turn_direction(s, e):
    """
    根据起点和终点的几何关系，判断是直行(^)、左转(<)还是右转(>)
    """
    # 将角度转换为弧度
    s_rad = math.radians(s['rotate'])
    e_rad = math.radians(e['rotate'])
    
    # 算起点的朝向单位向量 (CARLA 标准坐标系通常 x 朝前, y 朝右/左)
    # 这里用标准的 cos 和 sin 建立二维朝向向量
    v_start = (math.cos(s_rad), math.sin(s_rad))
    
    # 算从起点到终点的位移向量
    v_path = (e['x'] - s['x'], e['y'] - s['y'])
    path_len = math.sqrt(v_path[0]**2 + v_path[1]**2)
    
    if path_len == 0:
        return "^"
        
    # 归一化位移向量
    v_path_dir = (v_path[0] / path_len, v_path[1] / path_len)
    
    # 计算两个向量的二维外积 (Cross Product): A x B = x1*y2 - y1*x2
    # 在标准右手坐标系中：正数代表左转，负数代表右转（CARLA如果是左手系则反过来）
    # 为了保险，我们结合角度差做一个绝对安全的卡阈值判定
    diff = (e['rotate'] - s['rotate']) % 360
    
    # 直行判定：角度差很小（比如正负 30 度以内）
    if diff <= 35 or diff >= 325:
        return "^"
    
    # 左转与右转判定
    # 如果你的 CARLA 数据 90 度是右转，270 度是左转：
    if 35 < diff < 160:
        return ">"  # 右转
    elif 200 < diff < 325:
        return "<"  # 左转
        
    return "^"

def is_valid_path(s_rot, e_rot):
    # 计算角度差： (终点角度 - 起点角度) % 360
    diff = (e_rot - s_rot) % 360
    
    # 过滤掉头：如果角度差在 180 附近（例如 160-200 度），判定为掉头
    # 在标准的 CARLA 路口数据中，掉头通常正好是 180
    if 160 <= diff <= 200:
        return False
    
    # 额外逻辑：如果角度差为 0，且距离很近，可能是同向重复点，也可以过滤
    # 但因为你之前已经有了 dist > 10 的过滤，这里主要处理掉头
    return True

def generate_split_tasks(input_file):
    if not os.path.exists(input_file):
        print(f"找不到文件: {input_file}")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        all_towns = json.load(f)

    # 初始化两个库
    train_library = {}
    test_library = {}

    for town_name, categories in all_towns.items():
        for category_name, junctions in categories.items():
            # 确定当前属于哪种模式
            is_train = "train" in category_name
            target_lib = train_library if is_train else test_library
            
            if town_name not in target_lib:
                target_lib[town_name] = {}

            for junction_name, points in junctions.items():
                pairs = []
                starts = [p for p in points if p['start']]
                ends = [p for p in points if not p['start']]
                
                task_counter = 1
                for s in starts:
                    for e in ends:
                        dist = math.sqrt((s['x'] - e['x'])**2 + (s['y'] - e['y'])**2)

                        # 过滤掉距离太近的无效任务
                        if dist > 10 and is_valid_path(s['rotate'], e['rotate']):
                            direction_icon = get_turn_direction(s, e)
                            pairs.append({
                                "task_id": task_counter,
                                "direction": direction_icon,
                                "start_pose": s,
                                "target_pose": e,
                                "distance": round(dist, 2)
                            })
                            task_counter += 1
                
                if pairs:
                    target_lib[town_name][junction_name] = {
                        "junction_total": len(pairs),
                        "tasks": pairs
                    }

    # 分别保存两个文件
    with open(TRAIN_JSON, 'w', encoding='utf-8') as f:
        json.dump(train_library, f, indent=4, ensure_ascii=False)
    
    with open(TEST_JSON, 'w', encoding='utf-8') as f:
        json.dump(test_library, f, indent=4, ensure_ascii=False)
    
    print("成功！已生成 train_tasks.json 和 test_tasks.json")

# 执行
generate_split_tasks(INTESECTION_JSON)