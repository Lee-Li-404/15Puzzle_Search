from fifteen_state_class import State

def heuristic(s: State) -> int:
    # Precomputed goal row and column for each tile value.
    # Tile 0 is the blank tile.
    GOAL_R = (
        0, 0, 0, 0,
        1, 1, 1, 1,
        2, 2, 2, 2,
        3, 3, 3, 3
    )
    GOAL_C = (
        0, 1, 2, 3,
        0, 1, 2, 3,
        0, 1, 2, 3,
        0, 1, 2, 3
    )

    tiles = s.tiles
    manhattan_dist = 0

    # Calculate Manhattan Distance
    for i in range(16):
        val = tiles[i]
        if val == 0:  # Skip the blank tile
            continue

        goal_r = GOAL_R[val]
        goal_c = GOAL_C[val]
        cur_r, cur_c = divmod(i, 4)
        manhattan_dist += abs(goal_r - cur_r) + abs(goal_c - cur_c)

    linear_conflicts = 0

    # Calculate Linear Conflicts for rows
    for r in range(4):
        for c1 in range(4):
            val1 = tiles[r * 4 + c1]
            # Skip blank tile or tiles not in their goal row
            if val1 == 0 or GOAL_R[val1] != r:
                continue

            for c2 in range(c1 + 1, 4):
                val2 = tiles[r * 4 + c2]
                # Skip blank tile or tiles not in their goal row
                if val2 == 0 or GOAL_R[val2] != r:
                    continue

                # If val1 appears before val2 in the current row but its value is greater
                # (implies goal position is after val2's goal position in that row)
                if val1 > val2:
                    linear_conflicts += 1

    # Calculate Linear Conflicts for columns
    for c in range(4):
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            # Skip blank tile or tiles not in their goal column
            if val1 == 0 or GOAL_C[val1] != c:
                continue

            for r2 in range(r1 + 1, 4):
                val2 = tiles[r2 * 4 + c]
                # Skip blank tile or tiles not in their goal column
                if val2 == 0 or GOAL_C[val2] != c:
                    continue

                # If val1 appears before val2 in the current column but its value is greater
                # (implies goal position is after val2's goal position in that column)
                if val1 > val2:
                    linear_conflicts += 1

    # Evolving from heuristic_prev1 (score=0.0013, cost=1.776) which had
    # conflict_weight = 3.6, overall_weight = 3.18.
    # The current best (score=0.0006, cost=1.776) used
    # conflict_weight = 3.5, overall_weight = 3.2.
    # To further reduce generated nodes while staying within the cost_ratio bound (1.80),
    # we will aim for a slightly greedier heuristic. We will increase the conflict weight
    # to 3.55 and adjust the overall weight to 3.19.
    # This results in an effective heuristic of 3.19*MD + (3.55*3.19)*LC = 3.19*MD + 11.3245*LC.
    # This places slightly more emphasis on resolving conflicts, aiming for a better
    # pruning of the search space.
    conflict_weight = 3.55
    overall_weight = 3.19

    base_heuristic = manhattan_dist + conflict_weight * linear_conflicts

    # Return as an integer as required.
    return int(base_heuristic * overall_weight)
