from fifteen_state_class import State

def heuristic(s: State) -> int:
    GOAL_R = (0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3)
    GOAL_C = (0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3)

    tiles = s.tiles
    manhattan_dist = 0
    blank_pos = -1

    for i in range(16):
        val = tiles[i]
        if val == 0:
            blank_pos = i
            continue

        goal_r = GOAL_R[val]
        goal_c = GOAL_C[val]
        cur_r, cur_c = divmod(i, 4)
        manhattan_dist += abs(goal_r - cur_r) + abs(goal_c - cur_c)

    linear_conflicts = 0

    for r in range(4):
        for c1 in range(4):
            val1 = tiles[r * 4 + c1]
            if val1 == 0 or GOAL_R[val1] != r:
                continue

            for c2 in range(c1 + 1, 4):
                val2 = tiles[r * 4 + c2]
                if val2 == 0 or GOAL_R[val2] != r:
                    continue

                if val1 > val2:
                    linear_conflicts += 1

    for c in range(4):
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            if val1 == 0 or GOAL_C[val1] != c:
                continue

            for r2 in range(r1 + 1, 4):
                val2 = tiles[r2 * 4 + c]
                if val2 == 0 or GOAL_C[val2] != c:
                    continue

                if val1 > val2:
                    linear_conflicts += 1
    
    blank_r, blank_c = divmod(blank_pos, 4)
    blank_md = blank_r + blank_c

    conflict_weight = 3.5
    overall_weight = 3.2

    base_heuristic = manhattan_dist + conflict_weight * linear_conflicts
    
    final_h = int(base_heuristic * overall_weight + blank_md)

    return final_h