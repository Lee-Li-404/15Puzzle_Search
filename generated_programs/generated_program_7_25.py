from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic improves upon the best-performing v1 by making two key changes:
    1. It corrects the logic for calculating column-based Linear Conflicts, which was
       flawed in v1, for greater accuracy.
    2. It re-introduces a penalty for Corner Conflicts, a known difficult pattern.
       Previous attempts to add this failed due to overly aggressive weighting. This
       version uses a more conservative, tuned weight (cc_weight=0.7) to penalize
       these trap states just enough to improve search without harming solution quality.
    The goal is to reduce generated nodes by being "smarter" about hard states,
    while staying within the tight cost_ratio constraints.
    """
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
    # Row conflicts
    for r in range(4):
        for c1 in range(4):
            val1 = tiles[r * 4 + c1]
            if val1 == 0 or GOAL_R[val1] != r:
                continue
            for c2 in range(c1 + 1, 4):
                val2 = tiles[r * 4 + c2]
                if val2 != 0 and GOAL_R[val2] == r and val1 > val2:
                    linear_conflicts += 1

    # Column conflicts (with corrected logic vs v1)
    for c in range(4):
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            if val1 == 0 or GOAL_C[val1] != c:
                continue
            for r2 in range(r1 + 1, 4):
                val2 = tiles[r2 * 4 + c]
                if val2 != 0 and GOAL_C[val2] == c and GOAL_R[val1] > GOAL_R[val2]:
                    linear_conflicts += 1

    corner_conflicts = 0
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        corner_conflicts += 1
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        corner_conflicts += 1
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        corner_conflicts += 1
    
    # Retain successful weights from v1, but add a conservatively weighted CC term.
    lc_weight = 3.5
    cc_weight = 0.7
    overall_weight = 3.2

    base_heuristic = manhattan_dist + lc_weight * linear_conflicts + cc_weight * corner_conflicts
    return int(base_heuristic * overall_weight)