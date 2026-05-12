from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic evolves the current best-performing version (v1), which uses a
    heavily weighted combination of Manhattan Distance (MD) and a fast, albeit
    imperfect, Linear Conflicts (LC) calculation. The v1 heuristic is highly
    effective but operates very close to the cost_ratio limit, leaving little
    room for simple weight increases.

    This evolution introduces a new, targeted penalty for "locked-out tiles".
    This occurs when a corner tile's destination is occupied by its correct
    neighbors, making it very difficult to move the target tile into place.
    For example, if tiles 11 and 14 are in their goal positions, but tile 15 is
    not, tile 15 is "locked out" and requires significant maneuvering to place.

    By adding a specific, weighted penalty for this pattern on top of the successful
    v1 formula, the heuristic becomes "smarter" about avoiding these well-known
    trap states. This targeted adjustment aims to prune the search tree more
    effectively in difficult regions of the state space, reducing the number of
    generated nodes without a broad increase in the heuristic's value that would
    risk violating the cost_ratio constraint.
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
    # Uses the same imperfect but effective LC calculation from the high-performing v1.
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

    # New Feature: Locked-out tile penalty
    locked_out_penalty = 0
    if tiles[3] != 3 and tiles[2] == 2 and tiles[7] == 7:
        locked_out_penalty += 1
    if tiles[12] != 12 and tiles[8] == 8 and tiles[13] == 13:
        locked_out_penalty += 1
    if tiles[15] != 15 and tiles[11] == 11 and tiles[14] == 14:
        locked_out_penalty += 1
    
    lc_weight = 3.5
    locked_out_weight = 2.5
    overall_weight = 3.2

    base_heuristic = (manhattan_dist + 
                      lc_weight * linear_conflicts + 
                      locked_out_weight * locked_out_penalty)

    return int(base_heuristic * overall_weight)