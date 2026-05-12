from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic is an aggressive evolution of the Manhattan Distance plus
    Linear Conflicts (MD+LC) model. The goal is to drastically reduce the number
    of generated nodes by making the heuristic highly informed and non-admissible,
    while staying within the cost_ratio constraint of 1.80.

    It combines four components with aggressive weighting:
    1.  Manhattan Distance (MD): The standard base heuristic.
    2.  Weighted Linear Conflicts (LC): A very high weight of 7 is applied to
        each detected linear conflict. This heavily penalizes states where tiles
        are in the correct row/column but in the wrong order, as these are
        notoriously difficult to resolve.
    3.  Corner Conflict Penalty: A penalty is added for a specific difficult
        pattern where a corner tile is locked out of its goal position by two
        correctly placed adjacent tiles. This "last moves" type of penalty
        helps the search avoid these tricky local minima.
    4.  Long-Distance Penalty (LDP): A small bonus penalty for tiles that are
        very far (Manhattan distance >= 4) from their goal position. This helps
        prioritize states where more progress has been made.
    """
    GOAL_POS = (
        (0, 0), (0, 1), (0, 2), (0, 3),
        (1, 0), (1, 1), (1, 2), (1, 3),
        (2, 0), (2, 1), (2, 2), (2, 3),
        (3, 0), (3, 1), (3, 2), (3, 3)
    )

    tiles = s.tiles
    manhattan_distance = 0
    long_distance_penalty = 0

    # 1. Calculate MD and Long-Distance Penalty
    for i, val in enumerate(tiles):
        if val == 0:
            continue
        goal_r, goal_c = GOAL_POS[val]
        cur_r, cur_c = divmod(i, 4)
        md_tile = abs(goal_r - cur_r) + abs(goal_c - cur_c)
        manhattan_distance += md_tile
        if md_tile >= 4:
            long_distance_penalty += 1

    # 2. Calculate Linear Conflicts
    linear_conflicts = 0
    # Row conflicts
    for r in range(4):
        for c1 in range(4):
            val1 = tiles[r * 4 + c1]
            if val1 == 0 or GOAL_POS[val1][0] != r:
                continue
            for c2 in range(c1 + 1, 4):
                val2 = tiles[r * 4 + c2]
                if val2 != 0 and GOAL_POS[val2][0] == r and GOAL_POS[val1][1] > GOAL_POS[val2][1]:
                    linear_conflicts += 1
    # Column conflicts
    for c in range(4):
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            if val1 == 0 or GOAL_POS[val1][1] != c:
                continue
            for r2 in range(r1 + 1, 4):
                val2 = tiles[r2 * 4 + c]
                if val2 != 0 and GOAL_POS[val2][1] == c and GOAL_POS[val1][0] > GOAL_POS[val2][0]:
                    linear_conflicts += 1

    # 3. Calculate Corner Conflicts
    corner_conflicts = 0
    # Top-right corner (tile 3)
    if tiles[3] != 3 and tiles[2] == 2 and tiles[7] == 7:
        corner_conflicts += 1
    # Bottom-left corner (tile 12)
    if tiles[12] != 12 and tiles[8] == 8 and tiles[13] == 13:
        corner_conflicts += 1
    # Bottom-right corner (tile 15)
    if tiles[15] != 15 and tiles[11] == 11 and tiles[14] == 14:
        corner_conflicts += 1

    # 4. Combine components with aggressive weights
    # The cost_ratio of the previous best was low, allowing for a greedier heuristic.
    # We increase the LC weight and add a substantial corner penalty.
    return manhattan_distance + 7 * linear_conflicts + 4 * corner_conflicts + long_distance_penalty