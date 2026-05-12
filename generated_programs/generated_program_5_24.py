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

    # Check for row conflicts
    for r in range(4):
        for c1 in range(4):
            val1 = tiles[r * 4 + c1]
            # Only consider tiles that are not blank and belong in this row
            if val1 == 0 or GOAL_POS[val1][0] != r:
                continue

            for c2 in range(c1 + 1, 4):
                val2 = tiles[r * 4 + c2]
                # Only consider tiles that are not blank and belong in this row
                if val2 == 0 or GOAL_POS[val2][0] != r:
                    continue

                # Conflict: val1 and val2 are in the same row, in their goal row, but in the wrong order
                if val1 > val2:
                    linear_conflicts += 1

    # Check for column conflicts
    for c in range(4):
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            # Only consider tiles that are not blank and belong in this column
            if val1 == 0 or GOAL_POS[val1][1] != c:
                continue

            for r2 in range(r1 + 1, 4):
                val2 = tiles[r2 * 4 + c]
                # Only consider tiles that are not blank and belong in this column
                if val2 == 0 or GOAL_POS[val2][1] != c:
                    continue

                # Conflict: val1 and val2 are in the same column, in their goal column, but in the wrong order
                # (i.e., val1 should be below val2 in the goal state, but is currently above it)
                if val1 > val2:
                    linear_conflicts += 1

    # To improve upon the previous best (score=0.0006, cost=1.776, gen=0.001),
    # this heuristic slightly increases the linear conflict weight from 3.5 to 3.6.
    # This makes the heuristic more aggressive in penalizing linear conflicts,
    # aiming to further reduce the generated nodes while staying within the
    # cost_ratio bound. The overall weight remains the same to maintain balance.
    conflict_weight = 3.6
    overall_weight = 3.2

    base_heuristic = manhattan_dist + conflict_weight * linear_conflicts

    return int(base_heuristic * overall_weight)
