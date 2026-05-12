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
                if val2 == 0 or GOAL_POS[val2][0] != r:
                    continue

                if val1 > val2:
                    linear_conflicts += 1

    # Check for column conflicts
    for c in range(4):
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            if val1 == 0 or GOAL_POS[val1][1] != c:
                continue

            for r2 in range(r1 + 1, 4):
                val2 = tiles[r2 * 4 + c]
                if val2 == 0 or GOAL_POS[val2][1] != c:
                    continue

                if val1 > val2:
                    linear_conflicts += 1

    # Evolving from the previous best (heuristic_v1) by carefully rebalancing weights.
    # heuristic_v1 used conflict_weight = 3.5 and overall_weight = 3.2,
    # resulting in (3.2 * MD) + (3.2 * 3.5 * LC) = 3.2*MD + 11.2*LC.
    # With a cost_ratio near the limit (1.776 vs 1.80), blunt increases are risky.
    # This version slightly increases conflict_weight to emphasize linear conflicts
    # (which are high-cost impediments), while slightly decreasing overall_weight
    # to manage the total heuristic magnitude and keep cost_ratio in check.
    # The new effective heuristic becomes (3.18 * MD) + (3.18 * 3.6 * LC) = 3.18*MD + 11.448*LC.
    # This slightly reduces the MD component and slightly increases the LC component,
    # aiming for better pruning with minimal cost_ratio impact.
    conflict_weight = 3.6
    overall_weight = 3.18

    base_heuristic = manhattan_dist + conflict_weight * linear_conflicts

    return int(base_heuristic * overall_weight)