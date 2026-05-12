from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic evolves the best-performing family of prior solutions (v1, vr1),
    which are based on a weighted sum of Manhattan Distance (MD) and Linear
    Conflicts (LC). The goal is to further reduce the number of generated nodes by
    making the heuristic more aggressive, while staying within the cost_ratio limit.

    Analysis of previous attempts reveals key insights:
    1. `v1` (cw=3.5, ow=3.2) was the top performer with a cost_ratio of 1.776.
    2. `vr1` (cw=3.55, ow=3.2) improved on `v1`, showing that increasing the
       `conflict_weight` (cw) is an effective strategy.
    3. `vr2` (cw=3.57, ow=3.18) performed worse. This suggests that while increasing `cw`
       to 3.57 might have been beneficial, decreasing the `overall_weight` (ow) from
       the highly effective value of 3.2 was detrimental.

    This heuristic is based on the hypothesis that the `cw` increase in `vr2` was a
    good move, but it was coupled with a bad move (the `ow` decrease). Therefore,
    this version combines the best of both worlds: it adopts the more aggressive
    `conflict_weight` of 3.57 from `vr2` while retaining the proven `overall_weight`
    of 3.2 from the most successful versions (`v1` and `vr1`). This targeted change
    aims to maximize the heuristic's power in resolving complex tile conflicts,
    pushing the performance boundary just enough to reduce generated nodes without
    exceeding the solution quality constraint.
    """
    GOAL_POS = (
        (0, 0), (0, 1), (0, 2), (0, 3),
        (1, 0), (1, 1), (1, 2), (1, 3),
        (2, 0), (2, 1), (2, 2), (2, 3),
        (3, 0), (3, 1), (3, 2), (3, 3)
    )

    tiles = s.tiles
    manhattan_dist = 0

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
            if val1 == 0 or GOAL_POS[val1][0] != r:
                continue

            for c2 in range(c1 + 1, 4):
                val2 = tiles[r * 4 + c2]
                if val2 != 0 and GOAL_POS[val2][0] == r and val1 > val2:
                    linear_conflicts += 1

    # Check for column conflicts
    for c in range(4):
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            if val1 == 0 or GOAL_POS[val1][1] != c:
                continue

            for r2 in range(r1 + 1, 4):
                val2 = tiles[r2 * 4 + c]
                if val2 != 0 and GOAL_POS[val2][1] == c and val1 > val2:
                    linear_conflicts += 1

    conflict_weight = 3.57
    overall_weight = 3.2

    base_heuristic = manhattan_dist + conflict_weight * linear_conflicts

    return int(base_heuristic * overall_weight)