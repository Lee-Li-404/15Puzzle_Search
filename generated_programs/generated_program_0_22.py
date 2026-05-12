from fifteen_state_class import State

def heuristic(s: State) -> int:
    # This heuristic evolves the current best version (v1, score=0.0006) by
    # introducing a Weighted Manhattan Distance (WMD) to provide more nuanced
    # guidance to the A* search. The cost_ratio of v1 was 1.776, very close
    # to the 1.80 limit, so changes must be subtle.

    # The key idea is that tiles belonging to the bottom half of the board (8-15)
    # are generally harder to place correctly. WMD applies a small (5%) weight
    # increase to the Manhattan distance of these specific tiles. This encourages
    # the search to prioritize resolving the more difficult subproblems, aiming
    # to find a solution path more efficiently.

    # To maintain the strong performance from penalizing Linear Conflicts (LC), the
    # conflict weight is slightly increased. The final overall weight is then
    # carefully adjusted downwards to compensate for the general increase in the
    # heuristic's value, ensuring the cost_ratio remains within the bound. This
    # re-balancing act aims to reduce generated nodes without sacrificing
    # solution quality.
    
    GOAL_R = tuple(val // 4 for val in range(16))
    GOAL_C = tuple(val % 4 for val in range(16))

    tiles = s.tiles
    weighted_md = 0.0

    # Calculate Weighted Manhattan Distance
    for i, val in enumerate(tiles):
        if val == 0:
            continue

        goal_r = GOAL_R[val]
        dist = abs(goal_r - (i // 4)) + abs(GOAL_C[val] - (i % 4))
        
        # Apply a 5% weight to tiles belonging to the bottom half (rows 2 and 3)
        if goal_r >= 2:
            weighted_md += dist * 1.05
        else:
            weighted_md += dist

    linear_conflicts = 0

    # Row conflicts (using the efficient direct-comparison method)
    for r in range(4):
        for c1 in range(4):
            val1 = tiles[r * 4 + c1]
            if val1 == 0 or GOAL_R[val1] != r:
                continue
            for c2 in range(c1 + 1, 4):
                val2 = tiles[r * 4 + c2]
                if val2 != 0 and GOAL_R[val2] == r and val1 > val2:
                    linear_conflicts += 1

    # Column conflicts
    for c in range(4):
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            if val1 == 0 or GOAL_C[val1] != c:
                continue
            for r2 in range(r1 + 1, 4):
                val2 = tiles[r2 * 4 + c]
                if val2 != 0 and GOAL_C[val2] == c and val1 > val2:
                    linear_conflicts += 1

    # Weights are fine-tuned from the previous best (v1: conflict=3.5, overall=3.2)
    # This combination slightly increases the effective weights for both MD (for hard
    # tiles) and LC, making the heuristic slightly more aggressive and informed.
    conflict_weight = 3.55
    overall_weight = 3.17

    base_heuristic = weighted_md + conflict_weight * linear_conflicts
    
    return int(base_heuristic * overall_weight)