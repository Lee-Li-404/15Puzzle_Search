from fifteen_state_class import State

def heuristic(s: State) -> int:
    # Precomputed goal row and column for each tile value.
    # This is slightly more efficient than a tuple of tuples.
    GOAL_R = (0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3)
    GOAL_C = (0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3)

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
            if val1 == 0 or GOAL_R[val1] != r:
                continue

            for c2 in range(c1 + 1, 4):
                val2 = tiles[r * 4 + c2]
                if val2 == 0 or GOAL_R[val2] != r:
                    continue

                if val1 > val2:
                    linear_conflicts += 1

    # Calculate Linear Conflicts for columns
    for c in range(4):
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            if val1 == 0 or GOAL_C[val1] != c:
                continue

            for r2 in range(r1 + 1, 4):
                val2 = tiles[r2 * 4 + c]
                if val2 == 0 or GOAL_C[val2] != c:
                    continue

                if val1 > val2:
                    linear_conflicts += 1

    # The previous best (score=0.0006, cost=1.776) used weights that brought
    # the solution cost close to the 1.80 limit. Simply increasing greediness
    # is risky. This version attempts to improve node generation by rebalancing
    # the heuristic. It increases the emphasis on resolving complex linear
    # conflicts (conflict_weight: 3.5 -> 3.6) while slightly decreasing the
    # overall weight (overall_weight: 3.2 -> 3.18). This aims for a "smarter"
    # search that prioritizes unblocking tiles over pure distance, hopefully
    # finding solutions more directly without overshooting the cost bound.
    conflict_weight = 3.6
    overall_weight = 3.18

    base_heuristic = manhattan_dist + conflict_weight * linear_conflicts

    return int(base_heuristic * overall_weight)