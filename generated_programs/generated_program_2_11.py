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
            if val1 == 0 or GOAL_POS[val1][0] != r:
                continue

            for c2 in range(c1 + 1, 4):
                val2 = tiles[r * 4 + c2]
                if val2 == 0 or GOAL_POS[val2][0] != r:
                    continue

                # Conflict: val1 is to the left of val2, but val1's goal position
                # is to the right of val2's goal position in the same row.
                # (i.e., val1 has a larger goal index than val2)
                if val1 > val2:
                    linear_conflicts += 1

    # Check for column conflicts
    for c in range(4):
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            if val1 == 0 or GOAL_POS[val1][1] != c:
                continue

            for r2 in range(r1 + 1, 4):
                val2 = tiles[r2 * 4 + c]
                if val2 == 0 or GOAL_POS[val2][1] != c:
                    continue

                # Conflict: val1 is above val2, but val1's goal position
                # is below val2's goal position in the same column.
                # (i.e., val1 has a larger goal index than val2)
                if val1 > val2:
                    linear_conflicts += 1

    # The current best (score 0.0010) uses linear conflict weight 3.0 and overall weight 3.2.
    # To further reduce generated nodes, we will slightly increase the overall weight.
    # A small increment aims to make the search greedier, reducing node generation,
    # while carefully staying within the cost_ratio bound of 1.80.
    conflict_weight = 3.0
    overall_weight = 3.3 # Increased from 3.2

    base_heuristic = manhattan_dist + conflict_weight * linear_conflicts

    return int(base_heuristic * overall_weight)