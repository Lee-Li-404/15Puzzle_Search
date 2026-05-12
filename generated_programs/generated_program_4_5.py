from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    An advanced weighted heuristic for the 15-puzzle. This heuristic builds upon
    the successful combination of Manhattan Distance (MD) and Linear Conflicts (LC)
    by adding a new component: a Corner Conflict penalty, and slightly increasing
    the overall weight for greater greediness.

    - Manhattan Distance (MD): The standard sum of grid distances for each tile.
    - Linear Conflicts (LC): Penalizes tiles in their goal row/column but inverted.
    - Corner Conflicts: Adds a specific penalty for a common, hard-to-solve
      pattern where a tile is trapped in a corner by the tile that belongs there.
      This makes the base heuristic more informed about specific board layouts.
    - Weight (W): The combined, more accurate base heuristic is multiplied by a
      carefully tuned weight (1.75). The previous best had a cost_ratio of 1.219
      with a weight of 1.7, leaving significant room to be greedier before
      reaching the 1.80 limit. This change aims to reduce generated nodes.
    """
    # GOAL_RC[tile_value] -> (goal_row, goal_col). Pre-calculated for O(1) lookups.
    GOAL_RC = (
        (0, 0), (0, 1), (0, 2), (0, 3),
        (1, 0), (1, 1), (1, 2), (1, 3),
        (2, 0), (2, 1), (2, 2), (2, 3),
        (3, 0), (3, 1), (3, 2), (3, 3),
    )

    tiles = s.tiles
    manhattan_dist = 0

    # 1. Manhattan Distance Calculation
    for i in range(16):
        val = tiles[i]
        if val == 0:
            continue
        goal_r, goal_c = GOAL_RC[val]
        cur_r, cur_c = i // 4, i % 4
        manhattan_dist += abs(goal_r - cur_r) + abs(goal_c - cur_c)

    # 2. Linear Conflicts Calculation
    conflicts = 0
    # Row conflicts
    for r in range(4):
        for c1 in range(4):
            val1 = tiles[r * 4 + c1]
            if val1 == 0 or GOAL_RC[val1][0] != r:
                continue
            for c2 in range(c1 + 1, 4):
                val2 = tiles[r * 4 + c2]
                if val2 != 0 and GOAL_RC[val2][0] == r and val1 > val2:
                    conflicts += 1
    # Column conflicts
    for c in range(4):
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            if val1 == 0 or GOAL_RC[val1][1] != c:
                continue
            for r2 in range(r1 + 1, 4):
                val2 = tiles[r2 * 4 + c]
                if val2 != 0 and GOAL_RC[val2][1] == c and GOAL_RC[val1][0] > GOAL_RC[val2][0]:
                    conflicts += 1
    linear_conflicts_cost = conflicts * 2

    # 3. Corner Conflict Calculation
    # Penalizes cases where a corner is occupied by the wrong tile, and the
    # correct tile is in an adjacent spot, "locking" it in.
    corner_penalty = 0
    # Top-right corner (pos 3, tile 3)
    if tiles[3] != 3 and tiles[3] != 0:
        if tiles[2] == 3 or tiles[7] == 3:
            corner_penalty += 2
    # Bottom-left corner (pos 12, tile 12)
    if tiles[12] != 12 and tiles[12] != 0:
        if tiles[8] == 12 or tiles[13] == 12:
            corner_penalty += 2
    # Bottom-right corner (pos 15, tile 15)
    if tiles[15] != 15 and tiles[15] != 0:
        if tiles[11] == 15 or tiles[14] == 15:
            corner_penalty += 2

    # 4. Combine and Weight
    base_h = manhattan_dist + linear_conflicts_cost + corner_penalty

    # The weight is slightly increased from the previous best (1.7) to 1.75
    # to further reduce the search space, leveraging the ample headroom below
    # the cost_ratio limit of 1.80.
    WEIGHT = 1.75

    return int(base_h * WEIGHT)