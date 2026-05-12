from fifteen_state_class import State

def heuristic(s: State) -> int:
    GOAL_R = (0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3)
    GOAL_C = (0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3)

    tiles = s.tiles
    manhattan_dist = 0

    for i in range(16):
        val = tiles[i]
        if val == 0:
            continue
        cur_r, cur_c = divmod(i, 4)
        manhattan_dist += abs(GOAL_R[val] - cur_r) + abs(GOAL_C[val] - cur_c)

    linear_conflicts = 0
    for r in range(4):
        for c1 in range(4):
            val1 = tiles[r * 4 + c1]
            if val1 == 0 or GOAL_R[val1] != r:
                continue
            for c2 in range(c1 + 1, 4):
                val2 = tiles[r * 4 + c2]
                if val2 != 0 and GOAL_R[val2] == r and val1 > val2:
                    linear_conflicts += 1

    for c in range(4):
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            if val1 == 0 or GOAL_C[val1] != c:
                continue
            for r2 in range(r1 + 1, 4):
                val2 = tiles[r2 * 4 + c]
                if val2 != 0 and GOAL_C[val2] == c and val1 > val2:
                    linear_conflicts += 1

    corner_conflicts = 0
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        corner_conflicts += 1
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        corner_conflicts += 1
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        corner_conflicts += 1
    
    linear_conflict_weight = 3.9
    corner_conflict_weight = 2.5
    overall_weight = 3.1

    base_heuristic = (manhattan_dist + 
                      linear_conflict_weight * linear_conflicts +
                      corner_conflict_weight * corner_conflicts)
                      
    return int(base_heuristic * overall_weight)