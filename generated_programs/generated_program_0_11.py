from fifteen_state_class import State

def heuristic(s: State) -> int:
    # --- Constants and Lookup Tables ---
    # The previous best heuristic used (MD + 2*LC) * 3.4 and achieved a cost_ratio of 1.735.
    # To further reduce generated nodes, this heuristic strengthens the base estimate by
    # increasing the penalty for linear conflicts, which are a strong indicator of
    # required moves. The hypothesis is that a more accurate base heuristic will guide
    # the search more effectively.
    #
    # Base heuristic = Manhattan Distance + 3 * Linear Conflicts
    #
    # To compensate for the stronger base value and keep the cost_ratio <= 1.80, the
    # overall weight factor is recalibrated. A value of 3.2 is chosen, which is
    # more aggressive than previous attempts with lower weights but safer than the 3.4
    # weight applied to this stronger base.
    WEIGHT_FACTOR = 3.2
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
                mask |= (1 << c)
        
        if bin(mask).count('1') < 2:
            continue

        for c1 in range(4):
            if (mask >> c1) & 1:
                val1 = tiles[r * 4 + c1]
                goal_c1 = GOAL_COL[val1]
                for c2 in range(c1 + 1, 4):
                    if (mask >> c2) & 1:
                        val2 = tiles[r * 4 + c2]
                        if goal_c1 > GOAL_COL[val2]:
                            linear_conflicts += 1
    
    # Column Conflicts
    for c in range(4):
        mask = 0
        for r in range(4):
            val = tiles[r * 4 + c]
            if val != 0 and GOAL_COL[val] == c:
                mask |= (1 << r)

        if bin(mask).count('1') < 2:
            continue

        for r1 in range(4):
            if (mask >> r1) & 1:
                val1 = tiles[r1 * 4 + c]
                goal_r1 = GOAL_ROW[val1]
                for r2 in range(r1 + 1, 4):
                    if (mask >> r2) & 1:
                        val2 = tiles[r2 * 4 + c]
                        if goal_r1 > GOAL_ROW[val2]:
                            linear_conflicts += 1

    # Combine heuristic components and apply weighting
    base_h = manhattan_dist + (linear_conflicts * CONFLICT_FACTOR)
    
    return int(base_h * WEIGHT_FACTOR)