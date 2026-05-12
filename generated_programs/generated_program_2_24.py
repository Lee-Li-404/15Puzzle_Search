from fifteen_state_class import State

def heuristic(s: State) -> int:
    # Precomputed goal positions for faster lookups.
    # (row, col) for each tile value.
    GOAL_POS = (
        (0, 0), (0, 1), (0, 2), (0, 3),
        (1, 0), (1, 1), (1, 2), (1, 3),
        (2, 0), (2, 1), (2, 2), (2, 3),
        (3, 0), (3, 1), (3, 2), (3, 3)
    )

    tiles = s.tiles
    manhattan_dist = 0

    # Calculate Manhattan Distance for all tiles (except blank).
    for i in range(16):
        val = tiles[i]
        if val == 0:
            continue

        goal_r, goal_c = GOAL_POS[val]
        cur_r, cur_c = divmod(i, 4)
        manhattan_dist += abs(goal_r - cur_r) + abs(goal_c - cur_c)

    linear_conflicts = 0

    # Calculate linear conflicts for rows.
    for r in range(4):
        for c1 in range(4):
            val1 = tiles[r * 4 + c1]
            # Tile must be in its goal row to be part of a row conflict.
            if val1 == 0 or GOAL_POS[val1][0] != r:
                continue

            for c2 in range(c1 + 1, 4):
                val2 = tiles[r * 4 + c2]
                if val2 == 0 or GOAL_POS[val2][0] != r:
                    continue
                
                # If val1 is to the left of val2, but should be to the right.
                if val1 > val2:
                    linear_conflicts += 1

    # Calculate linear conflicts for columns.
    for c in range(4):
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            # Tile must be in its goal column to be part of a column conflict.
            if val1 == 0 or GOAL_POS[val1][1] != c:
                continue

            for r2 in range(r1 + 1, 4):
                val2 = tiles[r2 * 4 + c]
                if val2 == 0 or GOAL_POS[val2][1] != c:
                    continue

                # If val1 is above val2, but should be below.
                if val1 > val2:
                    linear_conflicts += 1

    # This heuristic evolves the previous best (score=0.0006, cost=1.776)
    # which used conflict_weight=3.5 and overall_weight=3.2.
    # To reduce generated nodes while staying under the cost_ratio of 1.80:
    # 1. Greediness is slightly increased: overall_weight is nudged from 3.2
    #    to 3.21. This aims to prune more nodes.
    # 2. Domain knowledge is added: A 'bonus' rewards placing key tiles
    #    (1, 4, 5) in their home positions. These form the top-left block,
    #    a difficult subproblem. Guiding the search towards this stable
    #    structure may improve search efficiency and offset the risk from
    #    the increased greediness.

    conflict_weight = 3.5
    overall_weight = 3.21

    base_heuristic = manhattan_dist + conflict_weight * linear_conflicts
    weighted_heuristic = base_heuristic * overall_weight

    # Bonus for locking in the key top-left corner tiles.
    bonus = 0
    if tiles[1] == 1:
        bonus += 5
    if tiles[4] == 4:
        bonus += 5
    if tiles[5] == 5:
        bonus += 5
        
    final_heuristic = int(weighted_heuristic - bonus)

    # The heuristic must return a non-negative integer.
    return max(0, final_heuristic)