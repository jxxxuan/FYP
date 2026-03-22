

def _compute_reward(self, prev_dist, curr_dist, velocity, collided, offroad, goal_reached):
    # 1. 碰撞惩罚 (Rc) [cite: 213]
    if collided:
        return -100.0
    
    # 2. 到达奖励 (Rg) [cite: 219]
    if goal_reached:
        return 100.0
    
    # 3. 距离进度 (Rd) [cite: 214]
    r_d = prev_dist - curr_dist
    
    # 4. 速度奖励 (Rv) - 限制在 0-30 m/s [cite: 217, 220]
    # 论文中 v_limit 为 30，奖励为 velocity / 10
    r_v = velocity / 10.0
    
    # 5. 车道/越界惩罚 (Ror, Rol) [cite: 218, 219]
    r_lane = -0.05 if offroad else 0.0
    
    # 总奖励聚合 [cite: 202]
    total_reward = r_d + r_v + r_lane
    return total_reward