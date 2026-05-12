from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic evolves the current best version (v1) by adding a third
    component: Corner Conflicts (CC). The v1 heuristic, based on Manhattan
    Distance (MD) and a heavily weighted Linear Conflicts (LC) term, is
    highly effective but operates close to the cost_ratio limit.

    Instead of simply increasing existing weights and risking a violation of
    the cost constraint, this version introduces a targeted penalty for a
    specific, difficult-to-resolve pattern: a corner tile in its correct
    place but blocked by incorrect adjacent tiles.

    By keeping the successful MD and LC weights from v1 and adding a small,
    carefully tuned CC term, the resulting heuristic h_new is strictly
    greater than or equal to the v1 heuristic for all states. This aims to
    prune the search tree more effectively by being "smarter" about known
    hard configurations, while introducing only a minimal increase to the
    heuristic's value to stay within the cost_ratio limit.
    """
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
        corner_conflicts += 1
    # Bottom-left corner (tile 12)
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        corner_conflicts += 1
    # Bottom-right corner (tile 15)
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        corner_conflicts += 1

    # Weights are based on the best heuristic (v1), with a new CC term added.
    lc_weight = 3.5
    cc_weight = 1.0 
    overall_weight = 3.2

    base_heuristic = manhattan_dist + lc_weight * linear_conflicts + cc_weight * corner_conflicts
    
    return int(base_heuristic * overall_weight)