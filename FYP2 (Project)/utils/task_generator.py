import json
import math
import os

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
                            pairs.append({
                                "task_id": task_counter,
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
    with open('train_tasks.json', 'w', encoding='utf-8') as f:
        json.dump(train_library, f, indent=4, ensure_ascii=False)
    
    with open('test_tasks.json', 'w', encoding='utf-8') as f:
        json.dump(test_library, f, indent=4, ensure_ascii=False)
    
    print("成功！已生成 train_tasks.json 和 test_tasks.json")

# 执行
generate_split_tasks('intersections.json')