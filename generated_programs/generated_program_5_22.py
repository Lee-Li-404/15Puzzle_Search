from fifteen_state_class import State

def heuristic(s: State) -> int:
    # Precompute goal rows and columns for all tiles (0-15)
    # This avoids repeated divmod calls or tuple lookups (GOAL_POS[val][0/1])
    # Tile 0 is at (0,0), Tile 1 at (0,1), ..., Tile 15 at (3,3)
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
        if val == 0:
            continue

        goal_r, goal_c = GOAL_R[val], GOAL_C[val]
        cur_r, cur_c = divmod(i, 4) # current row and column
        manhattan_dist += abs(goal_r - cur_r) + abs(goal_c - cur_c)

    linear_conflicts = 0

    # Check for row conflicts
    for r in range(4):
        for c1 in range(4):
            val1 = tiles[r * 4 + c1]
            # Only consider tiles that are not blank and belong in this row
            if val1 == 0 or GOAL_R[val1] != r:
                continue

            for c2 in range(c1 + 1, 4):
                val2 = tiles[r * 4 + c2]
                # Only consider tiles that are not blank and belong in this row
                if val2 == 0 or GOAL_R[val2] != r:
                    continue

                # Conflict: val1 and val2 are in the same row, in their goal row, but in the wrong order
                if val1 > val2:
                    linear_conflicts += 1

    # Check for column conflicts
    for c in range(4):
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            # Only consider tiles that are not blank and belong in this column
            if val1 == 0 or GOAL_C[val1] != c:
                continue

            for r2 in range(r1 + 1, 4):
                val2 = tiles[r2 * 4 + c]
                # Only consider tiles that are not blank and belong in this column
                if val2 == 0 or GOAL_C[val2] != c:
                    continue

                # Conflict: val1 and val2 are in the same column, in their goal column, but in the wrong order
                # (i.e., val1 should be below val2 in the goal state, but is currently above it)
                if val1 > val2:
                    linear_conflicts += 1

    # Tuned weights based on previous best performance (heuristic_v1).
    # The conflict_weight is slightly increased from 3.5 to 3.55 to make
    # the heuristic a bit greedier for linear conflicts. This aims to
    # further reduce generated nodes while keeping the cost_ratio below 1.80.
    conflict_weight = 3.55
    overall_weight = 3.2

    base_heuristic = manhattan_dist + conflict_weight * linear_conflicts

    return int(base_heuristic * overall_weight)