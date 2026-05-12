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

    # Check for row conflicts
    for r in range(4):
        for c1 in range(4):
            val1 = tiles[r * 4 + c1]
            # Skip blank tile or tiles not in their goal row
            if val1 == 0 or GOAL_POS[val1][0] != r:
                continue

            for c2 in range(c1 + 1, 4):
                val2 = tiles[r * 4 + c2]
                # Skip blank tile or tiles not in their goal row
                if val2 == 0 or GOAL_POS[val2][0] != r:
                    continue

                # If val1 appears before val2 in the current row but its goal position is after val2's goal position
                if val1 > val2:
                    linear_conflicts += 1

    # Check for column conflicts
    for c in range(4):
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            # Skip blank tile or tiles not in their goal column
            if val1 == 0 or GOAL_POS[val1][1] != c:
                continue

            for r2 in range(r1 + 1, 4):
                val2 = tiles[r2 * 4 + c]
                # Skip blank tile or tiles not in their goal column
                if val2 == 0 or GOAL_POS[val2][1] != c:
                    continue

                # If val1 appears before val2 in the current column but its goal position is after val2's goal position
                if val1 > val2:
                    linear_conflicts += 1

    base_heuristic = manhattan_dist + 2 * linear_conflicts

    # Increased weight for a greedier search, aiming to reduce generated nodes
    # while staying within the cost_ratio bound of 1.80. 
    # Previous best had a weight of 2.5, current best (score 0.0012) uses 2.5.
    # Trying a slightly higher weight to further push down generated nodes.
    weight = 2.9

    return int(base_heuristic * weight)