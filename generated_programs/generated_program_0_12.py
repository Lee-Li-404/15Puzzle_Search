from fifteen_state_class import State

def heuristic(s: State) -> int:
    # --- Constants and Lookup Tables ---
    # The previous best heuristic (`heuristic_v1`) used (MD + 3*LC) * 3.2 and achieved
    # a cost_ratio of 1.653, leaving a comfortable margin below the 1.80 limit.
    # To further reduce the number of generated nodes, this version makes the heuristic
    # greedier by increasing the overall weight factor.
    #
    # An increase from 3.2 to 3.35 is a calculated step. It increases the heuristic's
    # magnitude by approximately 4.7%, which should be well within the ~9% headroom
    # available in the cost_ratio (1.80 / 1.653 ≈ 1.09). This aims to aggressively
    # prune the search space while minimizing the risk of violating the cost constraint.
    WEIGHT_FACTOR = 3.35
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