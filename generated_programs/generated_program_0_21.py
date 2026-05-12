from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic builds upon the best-performing previous version (v1),
    which combines Manhattan Distance (MD) and Linear Conflicts (LC).
    The previous version achieved a cost_ratio of 1.776, leaving a small
    margin below the 1.80 limit.

    This evolution makes a fine-tuned adjustment to further reduce the number
    of generated nodes by leveraging this margin. The core insight from previous
    versions is that aggressively penalizing linear conflicts provides the best
    guidance to the A* search, significantly pruning the search space.

    The change is a slight increase in the `conflict_weight` from 3.5 to 3.55,
    while keeping the `overall_weight` at 3.2. This makes the heuristic even
    more sensitive to states with unresolved linear conflicts, guiding the search
    to prioritize their resolution more strongly. This targeted increase is a
    safer bet than a general increase in the overall weight, as it focuses the
    heuristic's power on the most challenging subproblems without inflating the
    value for simpler states as much, aiming for a better balance between greediness
    (fewer nodes) and solution quality (cost_ratio).
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

    # Increased conflict_weight from 3.5 to 3.55 to more aggressively
    # penalize difficult-to-resolve linear conflicts.
    conflict_weight = 3.55
    overall_weight = 3.2

    base_heuristic = manhattan_dist + conflict_weight * linear_conflicts

    return int(base_heuristic * overall_weight)