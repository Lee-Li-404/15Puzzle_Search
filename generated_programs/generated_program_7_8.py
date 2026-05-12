from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic enhances the Manhattan Distance with a highly weighted Linear
    Conflicts penalty and a new "long-distance" penalty. The goal is maximum
    reduction of generated nodes by creating a very aggressive, non-admissible
    heuristic that stays within the solution cost bounds.

    1. Manhattan Distance (MD): Base cost for each tile.
    2. Weighted Linear Conflicts (LC): A weight of 6 is applied to each conflict
       (tiles in their goal row/column but reversed). This aggressively prunes
       states with these hard-to-resolve configurations.
    3. Long-Distance Penalty: A small extra penalty is added for each tile with a
       Manhattan distance of 4 or more, targeting states where tiles are very
       far from home, which often require more complex move sequences.
    """
    GOAL_POS = (
        (0, 0), (0, 1), (0, 2), (0, 3),
        (1, 0), (1, 1), (1, 2), (1, 3),
        (2, 0), (2, 1), (2, 2), (2, 3),
        (3, 0), (3, 1), (3, 2), (3, 3)
    )

    manhattan_distance = 0
    long_distance_penalty = 0
    tiles = s.tiles

    # Calculate MD and long-distance penalty simultaneously.
    for i, val in enumerate(tiles):
        if val == 0:
            continue
        goal_r, goal_c = GOAL_POS[val]
        cur_r, cur_c = divmod(i, 4)
        
        md_tile = abs(goal_r - cur_r) + abs(goal_c - cur_c)
        manhattan_distance += md_tile
        
        if md_tile >= 4:
            long_distance_penalty += 1

    linear_conflicts = 0

    # Calculate row conflicts.
    for r in range(4):
        for c1 in range(4):
            val1 = tiles[r * 4 + c1]
            if val1 == 0 or GOAL_POS[val1][0] != r:
                continue
            for c2 in range(c1 + 1, 4):
                val2 = tiles[r * 4 + c2]
                if val2 != 0 and GOAL_POS[val2][0] == r and GOAL_POS[val1][1] > GOAL_POS[val2][1]:
                    linear_conflicts += 1

    # Calculate column conflicts.
    for c in range(4):
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            if val1 == 0 or GOAL_POS[val1][1] != c:
                continue
            for r2 in range(r1 + 1, 4):
                val2 = tiles[r2 * 4 + c]
                if val2 != 0 and GOAL_POS[val2][1] == c and GOAL_POS[val1][0] > GOAL_POS[val2][0]:
                    linear_conflicts += 1

    return manhattan_distance + 6 * linear_conflicts + long_distance_penalty