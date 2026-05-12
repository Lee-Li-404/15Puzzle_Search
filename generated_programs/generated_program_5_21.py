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
        row_tiles = [tiles[r * 4 + c] for c in range(4)]
        for c1 in range(4):
            val1 = row_tiles[c1]
            if val1 == 0 or GOAL_POS[val1][0] != r:
                continue

            for c2 in range(c1 + 1, 4):
                val2 = row_tiles[c2]
                if val2 == 0 or GOAL_POS[val2][0] != r:
                    continue

                if val1 > val2:
                    linear_conflicts += 1

    # Check for column conflicts
    for c in range(4):
        col_tiles = [tiles[r * 4 + c] for r in range(4)]
        for r1 in range(4):
            val1 = col_tiles[r1]
            if val1 == 0 or GOAL_POS[val1][1] != c:
                continue

            for r2 in range(r1 + 1, 4):
                val2 = col_tiles[r2]
                if val2 == 0 or GOAL_POS[val2][1] != c:
                    continue

                if val1 > val2:
                    linear_conflicts += 1

    # Apply weights: Increased Manhattan distance penalty, slightly increased linear conflict penalty
    # and a slightly higher overall greedy factor to push generated nodes down.
    # This aims to leverage the headroom in cost_ratio.
    md_weight = 1.0
    lc_weight = 3.5
    overall_weight = 3.3

    base_heuristic = manhattan_dist * md_weight + linear_conflicts * lc_weight

    return int(base_heuristic * overall_weight)