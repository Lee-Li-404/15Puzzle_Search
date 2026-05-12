from fifteen_state_class import State

def heuristic(s: State) -> int:
    # GOAL_RC[tile_value] -> (goal_row, goal_col). A tuple is faster for lookups.
    GOAL_RC = (
        (0, 0), (0, 1), (0, 2), (0, 3),  # 0-3
        (1, 0), (1, 1), (1, 2), (1, 3),  # 4-7
        (2, 0), (2, 1), (2, 2), (2, 3),  # 8-11
        (3, 0), (3, 1), (3, 2), (3, 3),  # 12-15
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

    # The weight is increased slightly from the previous best (1.7, score 0.0033)
    # to try and reduce generated nodes further. A weight of 1.8 was found to be
    # slightly worse (score 0.0035), suggesting the optimal point is between 1.7 and 1.8.
    # A small, conservative increment aims to capitalize on the available headroom
    # below the 1.80 cost_ratio bound.
    WEIGHT = 1.71

    return int(base_h * WEIGHT)