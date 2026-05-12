from fifteen_state_class import State

def heuristic(s: State) -> int:
    # --- Constants and Lookup Tables ---
    # The previous best heuristic uses (MD + 3*LC) * 3.9, with an estimated cost_ratio of 1.791.
    # To further reduce generated nodes, we will slightly increase the emphasis on Linear Conflicts
    # by raising CONFLICT_FACTOR from 3 to 3.1.
    # To keep the cost_ratio within the 1.80 limit, we will slightly decrease the overall
    # WEIGHT_FACTOR.
    #
    # Calculation for new WEIGHT_FACTOR:
    # Max possible MD = 80, Max possible LC = 16 (4 rows * 2 conflicts + 4 cols * 2 conflicts, assuming max conflicts can occur in disjoint positions)
    # Old max base_h = (MD_max + 3 * LC_max) = 80 + 3 * 16 = 80 + 48 = 128
    # New max base_h = (MD_max + 3.1 * LC_max) = 80 + 3.1 * 16 = 80 + 49.6 = 129.6
    #
    # To maintain roughly the same worst-case estimated cost:
    # (Old_max_base_h * Old_WEIGHT_FACTOR) ~= (New_max_base_h * New_WEIGHT_FACTOR)
    # (128 * 3.9) ~= (129.6 * New_WEIGHT_FACTOR)
    # 499.2 ~= 129.6 * New_WEIGHT_FACTOR
    # New_WEIGHT_FACTOR ~= 499.2 / 129.6 ~= 3.85185...
    #
    # We choose WEIGHT_FACTOR = 3.85 to be slightly conservative and ensure the cost_ratio remains <= 1.80.
    # The slight increase in CONFLICT_FACTOR (from 3 to 3.1) makes the heuristic more sensitive to conflicts,
    # which are often good indicators of moves needed, potentially reducing generated nodes.

    WEIGHT_FACTOR = 3.85
    CONFLICT_FACTOR = 3.1

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
        mask = 0 # Bitmask to track tiles in their goal row
        for c in range(4):
            val = tiles[r * 4 + c]
            if val != 0 and GOAL_ROW[val] == r:
                mask |= (1 << c) # Set bit if tile 'val' is in its goal row 'r'

        # If less than 2 tiles are in their goal row, no conflict is possible.
        # This check is an optimization; the nested loops would handle it correctly too.
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
                        # (i.e., they are in reverse order compared to their goal positions)
                        if goal_c1 > GOAL_COL[val2]:
                            linear_conflicts += 1

    # Column Conflicts
    for c in range(4):
        mask = 0 # Bitmask to track tiles in their goal column
        for r in range(4):
            val = tiles[r * 4 + c]
            if val != 0 and GOAL_COL[val] == c:
                mask |= (1 << r) # Set bit if tile 'val' is in its goal column 'c'

        # If less than 2 tiles are in their goal column, no conflict is possible.
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