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

    # Calculate Manhattan Distance
    for i in range(16):
        val = tiles[i]
        if val == 0:
            continue

        goal_r, goal_c = GOAL_POS[val]
        cur_r, cur_c = divmod(i, 4)
        manhattan_dist += abs(goal_r - cur_r) + abs(goal_c - cur_c)

    linear_conflicts = 0

    # Calculate Linear Conflicts for rows
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

                # If val1 appears before val2 in the current row but its goal position
                # is after val2's goal position in that same row.
                if val1 > val2:
                    linear_conflicts += 1

    # Calculate Linear Conflicts for columns
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

                # If val1 appears before val2 in the current column but its goal position
                # is after val2's goal position in that same column.
                if val1 > val2:
                    linear_conflicts += 1

    # The previous best (score=0.0006, cost=1.776) used conflict_weight=3.5, overall_weight=3.2.
    # This resulted in an effective heuristic of 3.2*MD + 11.2*LC.
    # To further reduce generated nodes while carefully staying within the 1.80 cost_ratio bound,
    # we slightly increase the overall_weight to 3.21. This makes the heuristic slightly
    # greedier, aiming for a minimal impact on solution cost while improving node generation efficiency.
    conflict_weight = 3.5
    overall_weight = 3.21

    base_heuristic = manhattan_dist + conflict_weight * linear_conflicts

    return int(base_heuristic * overall_weight)