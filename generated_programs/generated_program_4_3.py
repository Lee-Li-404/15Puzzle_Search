from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    A weighted heuristic combining Manhattan Distance and Linear Conflicts.
    - Manhattan Distance (MD): Sum of grid distances for each tile to its goal.
    - Linear Conflicts (LC): Adds cost for tiles in their goal row/column but in the wrong order.
    - Weight (W): The combined heuristic is multiplied by a weight W > 1 to make it
      greedier, aiming to reduce the number of generated nodes at the expense of
      guaranteed optimality, while staying within the cost_ratio bound.
    """
    # GOAL_RC[tile_value] -> (goal_row, goal_col). A tuple is faster for lookups.
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

    # Each conflict adds at least 2 moves to the optimal solution.
    linear_conflicts_cost = conflicts * 2

    # 3. Combine and Weight
    base_h = manhattan_dist + linear_conflicts_cost

    # A weight is applied to the admissible base heuristic (MD + LC) to prioritize
    # states that appear closer to the goal, reducing search space. The weight is
    # chosen to be aggressive but stay under the cost_ratio limit of 1.80.
    # The previous best heuristic used a weight of 1.7, with a cost_ratio of 1.219.
    # Increasing the weight to 1.9 aims to further reduce generated nodes while
    # remaining within the allowed cost_ratio of 1.80.
    WEIGHT = 1.9

    return int(base_h * WEIGHT)