from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    An evolved weighted heuristic combining Manhattan Distance and Linear Conflicts.
    This version enhances the penalty for Linear Conflicts (LC), as they often
    indicate more complex subproblems to solve than simple Manhattan Distance (MD)
    would suggest. The goal is to make the A* search greedier on states with
    these conflicts, resolving them faster to reduce the overall search space.

    - Manhattan Distance (MD): Sum of grid distances for each tile to its goal.
    - Linear Conflicts (LC): Detects pairs of tiles in their goal row/column
      but in the wrong order. This version increases the penalty for each
      conflict pair to 1.5 times the previous value (from 2 to 3).
    - Weight (W): An overall weight is applied to the combined heuristic to further
      reduce the number of generated nodes, while staying within the cost_ratio bound.
      The weight is kept at 1.7, which was successful previously, to balance the
      increased LC penalty and maintain solution quality.
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
    # A single loop is efficient O(N) where N=16.
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
            # Tile must be in its goal row to be part of a row conflict.
            if val1 == 0 or GOAL_RC[val1][0] != r:
                continue

            for c2 in range(c1 + 1, 4):
                val2 = tiles[r * 4 + c2]
                # If tile2 is also in its goal row and is inverted with tile1.
                if val2 != 0 and GOAL_RC[val2][0] == r and val1 > val2:
                    conflicts += 1

    # Column conflicts
    for c in range(4):
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            # Tile must be in its goal column to be part of a column conflict.
            if val1 == 0 or GOAL_RC[val1][1] != c:
                continue

            for r2 in range(r1 + 1, 4):
                val2 = tiles[r2 * 4 + c]
                # If tile2 is also in its goal column and is inverted with tile1.
                if val2 != 0 and GOAL_RC[val2][1] == c and GOAL_RC[val1][0] > GOAL_RC[val2][0]:
                    conflicts += 1

    # An admissible heuristic adds 2 moves per conflict. We increase this penalty
    # to 3 to prioritize resolving these difficult configurations more aggressively.
    linear_conflicts_cost = conflicts * 3

    # 3. Combine and Weight
    base_h = manhattan_dist + linear_conflicts_cost

    # The overall weight is chosen to balance greediness and solution quality.
    # The previous best heuristic used 1.7 successfully. We retain this weight
    # as the increased LC penalty already makes the base heuristic larger.
    WEIGHT = 1.7

    return int(base_h * WEIGHT)