from fifteen_state_class import State

def heuristic(s: State) -> int:
    # --- Constants and Lookup Tables ---
    # The best heuristic found so far uses (MD + 3*LC) * 3.6.
    # This achieved a score of 0.0008 with cost_ratio 1.653 (from round -2 eval).
    # To further reduce the number of generated nodes, we will slightly increase the
    # WEIGHT_FACTOR. The previous score was good, implying room to be greedier.
    # Increasing WEIGHT_FACTOR from 3.6 to 3.7.
    # The estimated new cost_ratio would be ~1.653 * (3.7 / 3.6) ≈ 1.705.
    # This remains well within the 1.80 limit.
    # The CONFLICT_FACTOR is kept at 3 as it's a reasonable weighting for linear conflicts.

    WEIGHT_FACTOR = 3.7
    CONFLICT_FACTOR = 3

    GOAL_ROW = (0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3)
    GOAL_COL = (0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3)

    # --- Calculation ---

    manhattan_dist = 0
    linear_conflicts = 0
    tiles = s.tiles

    # Calculate Manhattan Distance
    for i in range(16):
        val = tiles[i]
        if val != 0:
            goal_r, goal_c = GOAL_ROW[val], GOAL_COL[val]
            cur_r, cur_c = i // 4, i % 4
            manhattan_dist += abs(goal_r - cur_r) + abs(goal_c - cur_c)

    # Calculate Linear Conflicts using an efficient bitmask approach
    # Row Conflicts
    for r in range(4):
        mask = 0
        for c in range(4):
            val = tiles[r * 4 + c]
            if val != 0 and GOAL_ROW[val] == r:
                mask |= (1 << c) # Set bit if tile 'val' is in its goal row 'r'

        # A conflict requires at least two tiles in their goal row
        if bin(mask).count('1') < 2:
            continue

        for c1 in range(4):
            if (mask >> c1) & 1: # If tile at c1 is in its goal row
                val1 = tiles[r * 4 + c1]
                goal_c1 = GOAL_COL[val1]
                for c2 in range(c1 + 1, 4):
                    if (mask >> c2) & 1: # If tile at c2 is in its goal row
                        val2 = tiles[r * 4 + c2]
                        # If val1 appears before val2 but val1's goal column is after val2's goal column
                        if goal_c1 > GOAL_COL[val2]:
                            linear_conflicts += 1

    # Column Conflicts
    for c in range(4):
        mask = 0
        for r in range(4):
            val = tiles[r * 4 + c]
            if val != 0 and GOAL_COL[val] == c:
                mask |= (1 << r) # Set bit if tile 'val' is in its goal column 'c'

        # A conflict requires at least two tiles in their goal column
        if bin(mask).count('1') < 2:
            continue

        for r1 in range(4):
            if (mask >> r1) & 1: # If tile at r1 is in its goal column
                val1 = tiles[r1 * 4 + c]
                goal_r1 = GOAL_ROW[val1]
                for r2 in range(r1 + 1, 4):
                    if (mask >> r2) & 1: # If tile at r2 is in its goal column
                        val2 = tiles[r2 * 4 + c]
                        # If val1 appears before val2 but val1's goal row is after val2's goal row
                        if goal_r1 > GOAL_ROW[val2]:
                            linear_conflicts += 1

    # Combine heuristic components and apply weighting
    base_h = manhattan_dist + (linear_conflicts * CONFLICT_FACTOR)

    return int(base_h * WEIGHT_FACTOR)
