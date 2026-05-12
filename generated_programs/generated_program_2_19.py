from fifteen_state_class import State

def heuristic(s: State) -> int:
    # Precomputed goal row and column for each tile value.
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

    # The previous best (score=0.0006, generated=0.001, cost=1.776)
    # used conflict_weight = 3.5 and overall_weight = 3.2,
    # leading to an effective heuristic of 3.2*MD + 11.2*LC.
    # Subsequent attempts (e.g., heuristic_prev1) incrementally adjusted these
    # to conflict_weight = 3.65 and overall_weight = 3.18,
    # resulting in 3.18*MD + 11.607*LC.
    # To further reduce generated nodes while staying within the tight cost_ratio bound (1.80),
    # we continue this cautious trend. We slightly increase conflict_weight to 3.66
    # and slightly decrease overall_weight to 3.17.
    # This results in an effective heuristic of 3.17*MD + (3.66 * 3.17)*LC = 3.17*MD + 11.6122*LC.
    # This re-balances the heuristic to be marginally more aggressive in penalizing linear conflicts,
    # aiming to prune more branches without significantly impacting solution length.
    conflict_weight = 3.66
    overall_weight = 3.17

    base_heuristic = manhattan_dist + conflict_weight * linear_conflicts

    return int(base_heuristic * overall_weight)