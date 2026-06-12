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
    According to the geometric relationship of the starting point and ending point, determine if it is straight (^), left turn (<) or right turn (>)
    """
    # Convert angle to radians
    s_rad = math.radians(s['rotate'])
    e_rad = math.radians(e['rotate'])
    
    # Calculate starting heading unit vector (CARLA standard coordinate system usually has x forward, y right/left)
    # Use standard cos and sin to establish 2D heading vector
    v_start = (math.cos(s_rad), math.sin(s_rad))
    
    # Calculate displacement vector from start to target
    v_path = (e['x'] - s['x'], e['y'] - s['y'])
    path_len = math.sqrt(v_path[0]**2 + v_path[1]**2)
    
    if path_len == 0:
        return "^"
        
    # Normalize displacement vector
    v_path_dir = (v_path[0] / path_len, v_path[1] / path_len)
    
    # Calculate the 2D cross product of two vectors: A x B = x1*y2 - y1*x2
    # In a standard right-handed coordinate system: positive represents a left turn, negative represents a right turn (reversed if CARLA uses left-handed)
    # To be safe, we combine the angle difference to make a safe threshold decision
    diff = (e['rotate'] - s['rotate']) % 360
    
    # Straight judgment: angle difference is very small (e.g., within plus or minus 35 degrees)
    if diff <= 35 or diff >= 325:
        return "^"
    
    # Left turn and right turn judgment
    # If your CARLA data has 90 degrees as right turn and 270 degrees as left turn:
    if 35 < diff < 160:
        return ">"  # Right turn
    elif 200 < diff < 325:
        return "<"  # Left turn
        
    return "^"

def is_valid_path(s_rot, e_rot):
    # Calculate angle difference: (Target angle - Start angle) % 360
    diff = (e_rot - s_rot) % 360
    
    # Filter out U-turns: if the angle difference is around 180 (e.g., 160-200 degrees), it is judged as a U-turn
    # In standard CARLA junction data, U-turns are usually exactly 180
    if 160 <= diff <= 200:
        return False
    
    # Extra logic: if angle difference is 0 and distance is very close, it might be a duplicate point in the same direction, which can also be filtered
    # But since you already filtered by dist > 10 earlier, this mainly handles U-turns
    return True

def generate_split_tasks(input_file):
    if not os.path.exists(input_file):
        print(f"File not found: {input_file}")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        all_towns = json.load(f)

    # Initialize two libraries
    train_library = {}
    test_library = {}

    for town_name, categories in all_towns.items():
        for category_name, junctions in categories.items():
            # Determine which mode current belongs to
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

                        # Filter out invalid tasks that are too close
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

    # Save two files respectively
    with open(TRAIN_JSON, 'w', encoding='utf-8') as f:
        json.dump(train_library, f, indent=4, ensure_ascii=False)
    
    with open(TEST_JSON, 'w', encoding='utf-8') as f:
        json.dump(test_library, f, indent=4, ensure_ascii=False)
    
    print("Success! Generated train_tasks.json and test_tasks.json")
 
# Execute
generate_split_tasks(INTESECTION_JSON)