from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic improves upon the best previous version (based on MD + LC) by
    integrating a third component: Corner Conflicts (CC). A tile in its goal
    corner is considered a conflict if its adjacent tiles (which also belong in
    that corner) are not in place, as this forms a difficult-to-resolve block.

    To accommodate this new, additive penalty term without exceeding the cost_ratio
    limit (<= 1.80), the overall greedy weighting factor has been slightly reduced
    from 3.2 to 3.15. This rebalances the heuristic to be less uniformly aggressive
    and more targeted, applying strong penalties specifically to states with known
    hard patterns (linear and corner conflicts). The goal is to create a "smarter"
    heuristic that prunes the search tree more effectively, thereby reducing the
    number of generated nodes.
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
    # Row conflicts
    for r in range(4):
        for c1 in range(4):
            val1 = tiles[r * 4 + c1]
            if val1 == 0 or GOAL_POS[val1][0] != r:
                continue
            for c2 in range(c1 + 1, 4):
                val2 = tiles[r * 4 + c2]
                if val2 != 0 and GOAL_POS[val2][0] == r and val1 > val2:
                    linear_conflicts += 1

    # Column conflicts
    for c in range(4):
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            if val1 == 0 or GOAL_POS[val1][1] != c:
                continue
            for r2 in range(r1 + 1, 4):
                val2 = tiles[r2 * 4 + c]
                if val2 != 0 and GOAL_POS[val2][1] == c and val1 > val2:
                    linear_conflicts += 1

    corner_conflicts = 0
    # Top-right corner (tile 3 at index 3)
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        corner_conflicts += 1
    # Bottom-left corner (tile 12 at index 12)
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        corner_conflicts += 1
    # Bottom-right corner (tile 15 at index 15)
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        corner_conflicts += 1

    lc_weight = 3.5
    cc_weight = 2.0
    overall_weight = 3.15

    base_heuristic = manhattan_dist + lc_weight * linear_conflicts + cc_weight * corner_conflicts

    return int(base_heuristic * overall_weight)