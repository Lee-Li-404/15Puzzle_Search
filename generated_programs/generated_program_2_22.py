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

                # If val1 appears before val2 in the current row but its goal position
                # is after val2's goal position in that same row, it's a conflict.
                # Since values correspond to goal positions (e.g., tile 1 goal_c=1, tile 2 goal_c=2),
                # val1 > val2 directly implies val1's goal is after val2's goal within the row.
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

                # If val1 appears before val2 in the current column but its goal position
                # is after val2's goal position in that same column, it's a conflict.
                if val1 > val2:
                    linear_conflicts += 1

    # This heuristic is based on the previous best (score=0.0006, cost=1.776).
    # That heuristic used conflict_weight=3.5 and overall_weight=3.2.
    # To further reduce generated nodes while ensuring the cost_ratio stays below 1.80,
    # we will slightly increase the linear_conflicts weight and decrease the
    # overall multiplier. This makes the heuristic slightly greedier by
    # emphasizing the resolution of more complex linear conflicts, aiming to
    # prune more branches without significantly impacting solution length.
    # New weights: conflict_weight=3.6, overall_weight=3.18.
    # This results in an effective heuristic of 3.18*MD + 11.52*LC.
    conflict_weight = 3.6
    overall_weight = 3.18

    base_heuristic = manhattan_dist + conflict_weight * linear_conflicts

    # Return as an integer as required.
    return int(base_heuristic * overall_weight)