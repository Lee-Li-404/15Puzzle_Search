from fifteen_state_class import State

def heuristic(s: State) -> int:
    GOAL_POS = (
        (0, 0), (0, 1), (0, 2), (0, 3),
        (1, 0), (1, 1), (1, 2), (1, 3),
        (2, 0), (2, 1), (2, 2), (2, 3),
        (3, 0), (3, 1), (3, 2), (3, 3)
    )

    tiles = s.tiles
    manhattan_dist = 0

    for i in range(16):
        val = tiles[i]
        if val == 0:
            continue
        goal_r, goal_c = GOAL_POS[val]
        cur_r, cur_c = divmod(i, 4)
        manhattan_dist += abs(goal_r - cur_r) + abs(goal_c - cur_c)

    linear_conflicts = 0

    # Row conflicts
    for r in range(4):
        for c1 in range(4):
            val1 = tiles[r * 4 + c1]
            if val1 == 0 or GOAL_POS[val1][0] != r:
                continue
            for c2 in range(c1 + 1, 4):
                val2 = tiles[r * 4 + c2]
                if val2 != 0 and GOAL_POS[val2][0] == r and val1 > val2:
                    linear_conflicts += 1

    # Column conflicts
    for c in range(4):
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            if val1 == 0 or GOAL_POS[val1][1] != c:
                continue
            for r2 in range(r1 + 1, 4):
                val2 = tiles[r2 * 4 + c]
                if val2 != 0 and GOAL_POS[val2][1] == c and val1 > val2:
                    linear_conflicts += 1

    corner_conflicts = 0
    # Top-right corner (tile 3)
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        corner_conflicts += 2
    # Bottom-left corner (tile 12)
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        corner_conflicts += 2
    # Bottom-right corner (tile 15)
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        corner_conflicts += 2
        
    # This heuristic evolves the previous best by adding a Corner Conflict (CC) term
    # and re-balancing the weights to make the search "smarter" about hard patterns.
    # The previous best had a cost_ratio of 1.776, close to the 1.80 limit. To add the
    # CC term without exceeding the limit, the overall weight is slightly reduced while
    # the linear conflict weight is slightly increased, shifting focus to resolving
    # tile blockages.
    conflict_weight = 3.6
    overall_weight = 3.15
    
    base_heuristic = manhattan_dist + conflict_weight * linear_conflicts + corner_conflicts
    
    return int(base_heuristic * overall_weight)