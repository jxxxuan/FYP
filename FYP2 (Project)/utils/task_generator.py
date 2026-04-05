import json
import math

def generate_tasks_file(input_file, output_file):
    # 1. 读取原始路口数据
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            all_towns = json.load(f)
    except FileNotFoundError:
        print(f"错误：找不到文件 {input_file}")
        return

    final_task_library = {}

    # 2. 遍历每一个地图 (Town03, Town04, Town05...)
    for town_name, intersections in all_towns.items():
        final_task_library[town_name] = {}
        
        # 3. 遍历每一个路口 (T intersection 1, Parking...)
        for junction_name, points in intersections.items():
            pairs = []
            starts = [p for p in points if p['start']]
            ends = [p for p in points if not p['start']]
            
            # 4. 执行配对逻辑
            for s in starts:
                for e in ends:
                    dist = math.sqrt((s['x'] - e['x'])**2 + (s['y'] - e['y'])**2)
                    
                    # 距离过滤：路口任务通常在 15-50米 比较合理
                    if dist > 10:
                        pairs.append({
                            "start_pose": s,
                            "target_pose": e,
                            "distance": round(dist, 2)
                        })
            
            final_task_library[town_name][junction_name] = {
                "total_paths": len(pairs),
                "tasks": pairs
            }

    # 5. 保存生成的任务库
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_task_library, f, indent=4, ensure_ascii=False)
    
    print(f"成功！已将任务对保存至: {output_file}")

# 执行
generate_tasks_file(r'../intersections.json', r'../tasks.json')