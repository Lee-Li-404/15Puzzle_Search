from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic evolves the previous best version by introducing a Corner Conflict (CC) term,
    creating a more informed heuristic function. The goal is to reduce the number of generated nodes
    while staying within the cost_ratio limit of 1.80.

    It combines three components:
    1. Manhattan Distance (MD): The standard sum of distances for each tile.
    2. Linear Conflicts (LC): Penalizes tiles in their correct row/column but in the wrong order.
    3. Corner Conflicts (CC): Adds a specific penalty for when a corner tile is in place but blocks
       adjacent tiles from moving into their goal positions, a situation requiring significant moves to resolve.

    The weighting is carefully adjusted to incorporate the new CC term without exceeding the cost_ratio bound.
    The overall weight is slightly reduced from the previous best, while the LC weight is increased, 
    and a substantial weight is given to the new CC term. This rebalancing aims to make the search more 
    greedy in a "smarter" way, prioritizing the resolution of complex board states.
    """
    
    GOAL_POS = (
        (0, 0), (0, 1), (0, 2), (0, 3),
        (1, 0), (1, 1), (1, 2), (1, 3),
        (2, 0), (2, 1), (2, 2), (2, 3),
        (3, 0), (3, 1), (3, 2), (3, 3)
    )

    tiles = s.tiles
    manhattan_dist = 0
    
    # 1. Manhattan Distance
    for i in range(16):
        val = tiles[i]
        if val == 0:
            continue
        goal_r, goal_c = GOAL_POS[val]
        cur_r, cur_c = divmod(i, 4)
        manhattan_dist += abs(goal_r - cur_r) + abs(goal_c - cur_c)

    # 2. Linear Conflicts (each conflict pair counts as 1)
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
                    
    # 3. Corner Conflicts (each locked corner counts as 1)
    corner_conflicts = 0
    # Top-right corner (tile 3, needs 2 and 7)
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        corner_conflicts += 1
    # Bottom-left corner (tile 12, needs 8 and 13)
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        corner_conflicts += 1
    # Bottom-right corner (tile 15, needs 11 and 14)
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        corner_conflicts += 1

    # 4. Combine with tuned weights
    lc_weight = 3.6
    cc_weight = 3.0
    overall_weight = 3.15

    base_heuristic = manhattan_dist + lc_weight * linear_conflicts + cc_weight * corner_conflicts
    
    return int(base_heuristic * overall_weight)