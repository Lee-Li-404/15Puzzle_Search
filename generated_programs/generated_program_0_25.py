from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic evolves the best-performing previous version (v1), which
    effectively combined Manhattan Distance (MD) and Linear Conflicts (LC).
    The key challenge is that v1's cost_ratio (1.776) was very close to the
    1.80 limit, making it risky to simply increase the heuristic's overall greediness.

    This evolution aims to make the heuristic "smarter" by introducing a new,
    targeted feature: Corner Conflicts (CC). This term identifies specific,
    hard-to-resolve end-game patterns where a corner tile is in its correct
    place but its adjacent, out-of-place tiles are trapped. This scenario is
    often underestimated by MD and LC alone.

    To integrate this new feature without exceeding the cost_ratio bound, the
    weights have been carefully re-balanced from v1's successful formula:
    1. A `corner_weight` is added to penalize these locked corner states.
    2. The `conflict_weight` for LC is slightly increased (3.5 -> 3.6) to
       maintain strong pressure on resolving complex tile interactions.
    3. The `overall_weight` is slightly reduced (3.2 -> 3.1) to create
       headroom for the new CC term, keeping the heuristic's magnitude in check.

    The goal is to provide more nuanced guidance to the A* search, pruning
    more of the search tree in difficult states to reduce generated nodes,
    while maintaining high-quality (low-cost) solutions.
    """
    GOAL_POS = (
        (0, 0), (0, 1), (0, 2), (0, 3),
        (1, 0), (1, 1), (1, 2), (1, 3),
        (2, 0), (2, 1), (2, 2), (2, 3),
        (3, 0), (3, 1), (3, 2), (3, 3)
    )

    tiles = s.tiles
    manhattan_dist = 0

    # Calculate Manhattan Distance for all tiles
    for i in range(16):
        val = tiles[i]
        if val == 0:
            continue
        goal_r, goal_c = GOAL_POS[val]
        cur_r, cur_c = divmod(i, 4)
        manhattan_dist += abs(goal_r - cur_r) + abs(goal_c - cur_c)

    linear_conflicts = 0
    # Check for row conflicts
    for r in range(4):
        for c1 in range(4):
            val1 = tiles[r * 4 + c1]
            if val1 == 0 or GOAL_POS[val1][0] != r:
                continue
            for c2 in range(c1 + 1, 4):
                val2 = tiles[r * 4 + c2]
                if val2 != 0 and GOAL_POS[val2][0] == r and val1 > val2:
                    linear_conflicts += 1

    # Check for column conflicts
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
    
    # Weighting scheme based on empirical tuning from prior best versions
    conflict_weight = 3.6
    corner_weight = 2.0
    overall_weight = 3.1

    base_heuristic = manhattan_dist + \
                     conflict_weight * linear_conflicts + \
                     corner_weight * corner_conflicts

    return int(base_heuristic * overall_weight)