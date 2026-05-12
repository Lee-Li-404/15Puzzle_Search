from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic aims to reduce generated nodes by aggressively penalizing
    states that are difficult to resolve, while staying within the cost_ratio limit.

    It combines: 
    1. Manhattan Distance (MD): Standard admissible heuristic.
    2. Linear Conflicts (LC): Penalizes tiles in the same row/column that are
       in the wrong order relative to their goal positions. Weighted by 6.
    3. Corner Conflicts (CC): Penalizes specific corner tiles (3, 12, 15) if they are
       in their goal position but block adjacent tiles. Penalty is 2.
    4. Aggressive Overall Weighting: A high weighting factor of 3.5 is applied
       to inflate the heuristic value, making A* more greedy and pruning more nodes.
       This factor is increased from previous versions to leverage remaining headroom
       in the cost_ratio bound.

    The formula is: `int((MD + LC * 6 + CC) * 3.5)`.
    This approach is derived from successful strategies in previous iterations,
    focusing on increasing the greedy nature of the heuristic to minimize generated nodes.
    """

    MD_TABLE = (
        (0, 1, 2, 3, 1, 2, 3, 4, 2, 3, 4, 5, 3, 4, 5, 6),
        (1, 0, 1, 2, 2, 1, 2, 3, 3, 2, 3, 4, 4, 3, 4, 5),
        (2, 1, 0, 1, 3, 2, 1, 2, 4, 3, 2, 3, 5, 4, 3, 4),
        (3, 2, 1, 0, 4, 3, 2, 1, 5, 4, 3, 2, 6, 5, 4, 3),
        (1, 2, 3, 4, 0, 1, 2, 3, 1, 2, 3, 4, 2, 3, 4, 5),
        (2, 1, 2, 3, 1, 0, 1, 2, 2, 1, 2, 3, 3, 2, 3, 4),
        (3, 2, 1, 2, 2, 1, 0, 1, 3, 2, 1, 2, 4, 3, 2, 3),
        (4, 3, 2, 1, 3, 2, 1, 0, 4, 3, 2, 1, 5, 4, 3, 2),
        (2, 3, 4, 5, 1, 2, 3, 4, 0, 1, 2, 3, 1, 2, 3, 4),
        (3, 2, 3, 4, 2, 1, 2, 3, 1, 0, 1, 2, 2, 1, 2, 3),
        (4, 3, 2, 3, 3, 2, 1, 2, 2, 1, 0, 1, 3, 2, 1, 2),
        (5, 4, 3, 2, 4, 3, 2, 1, 3, 2, 1, 0, 4, 3, 2, 1),
        (3, 4, 5, 6, 2, 3, 4, 5, 1, 2, 3, 4, 0, 1, 2, 3),
        (4, 3, 4, 5, 3, 2, 3, 4, 2, 1, 2, 3, 1, 0, 1, 2),
        (5, 4, 3, 4, 4, 3, 2, 3, 3, 2, 1, 2, 2, 1, 0, 1),
        (6, 5, 4, 3, 5, 4, 3, 2, 4, 3, 2, 1, 3, 2, 1, 0)
    )

    GOAL_R = (0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3)
    GOAL_C = (0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3)

    tiles = s.tiles

    md = 0
    for i, val in enumerate(tiles):
        if val != 0:
            md += MD_TABLE[i][val]

    lc = 0
    # Row conflicts
    for r in range(4):
        for c1 in range(4):
            val1 = tiles[r * 4 + c1]
            if val1 == 0 or GOAL_R[val1] != r:
                continue
            for c2 in range(c1 + 1, 4):
                val2 = tiles[r * 4 + c2]
                if val2 != 0 and GOAL_R[val2] == r and val1 > val2:
                    lc += 2
    # Column conflicts
    for c in range(4):
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            if val1 == 0 or GOAL_C[val1] != c:
                continue
            for r2 in range(r1 + 1, 4):
                val2 = tiles[r2 * 4 + c]
                if val2 != 0 and GOAL_C[val2] == c and GOAL_R[val1] > GOAL_R[val2]:
                    lc += 2

    cc = 0
    # Corner Conflicts: Penalize tiles if they are in a corner but block other tiles.
    # Top-right corner (tile 3)
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        cc += 2
    # Bottom-left corner (tile 12)
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        cc += 2
    # Bottom-right corner (tile 15)
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        cc += 2

    # Combine all components. Linear conflicts are weighted more heavily (lc * 6).
    base_h = md + lc * 6 + cc

    # Apply an overall greedy weighting factor to further inflate the heuristic.
    # Increased from 3.4 to 3.5 to maximize node reduction while attempting to stay within cost_ratio limits.
    return int(base_h * 3.5)
