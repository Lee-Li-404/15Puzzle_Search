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

    # Calculate Manhattan distance
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
            # Skip blank tile or tiles not in their goal row
            if val1 == 0 or GOAL_POS[val1][0] != r:
                continue

            for c2 in range(c1 + 1, 4):
                val2 = tiles[r * 4 + c2]
                # Skip blank tile or tiles not in their goal row
                if val2 == 0 or GOAL_POS[val2][0] != r:
                    continue

                # If val1 appears before val2 in the current row but its value is greater
                # (implies goal position is after val2's goal position in that row)
                if val1 > val2:
                    linear_conflicts += 1

    # Check for column conflicts
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

                # If val1 appears before val2 in the current column but its value is greater
                # (implies goal position is after val2's goal position in that column)
                if val1 > val2:
                    linear_conflicts += 1

    # Based on the best performing heuristics (v1 and vr2), a weighted sum of
    # Manhattan distance and linear conflicts is effective. The previous best
    # (score=0.0006) used a conflict weight of 3.5 and an overall multiplier of 3.2.
    # To further reduce generated nodes, we'll increase the weight assigned to
    # linear conflicts, as they represent more complex situations that A* struggles with.
    # Increasing conflict_weight from 3.5 to 3.6 and slightly adjusting the overall
    # multiplier to 3.19 aims for a slightly greedier heuristic that prioritizes
    # resolving these conflicts, hoping to prune more branches without exceeding
    # the cost_ratio bound. This gives an effective heuristic of 3.19*MD + 11.544*LC.
    conflict_weight = 3.6
    overall_weight = 3.19

    base_heuristic = manhattan_dist + conflict_weight * linear_conflicts

    return int(base_heuristic * overall_weight)