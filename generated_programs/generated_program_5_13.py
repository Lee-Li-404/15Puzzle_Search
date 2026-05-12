from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic further refines the successful Manhattan Distance (MD) + Linear Conflicts (LC)
    + Corner Conflicts (CC) combination, pushing the greediness slightly higher to reduce
    the number of generated nodes while staying within the cost_ratio bound.

    Building upon the previous best (generated=0.001, cost=1.612), this version makes
    the following controlled adjustments:

    1. Linear Conflict Weight: The multiplier for linear conflicts remains at 6 (`lc * 6`).
       This specific weight has shown to be effective in penalizing states with difficult
       in-row/in-column misplacements, which are costly to resolve.

    2. Increased Overall Greedy Multiplier: The final scaling factor is slightly increased
       from 3.1 (in previous attempts) to 3.2. This inflates the total heuristic value,
       making the A* search more aggressive in pruning less promising branches.
       Given the comfortable headroom in the cost_ratio (1.612 against a 1.80 limit),
       this incremental increase aims to further reduce the `generated_ratio` without
       exceeding the cost constraint.

    The precomputed MD_TABLE, GOAL_R, and GOAL_C ensure efficiency.
    Linear conflicts are detected when two tiles are in their respective goal row/column
    but are inverted in order. Corner conflicts are detected for specific corner tiles
    (3, 12, 15) if they are in place but block adjacent tiles.
    """
    MD_TABLE = tuple(
        tuple(
            abs((i // 4) - (val // 4)) + abs((i % 4) - (val % 4))
            for val in range(16)
        )
        for i in range(16)
    )
    GOAL_R = tuple(val // 4 for val in range(16))
    GOAL_C = tuple(val % 4 for val in range(16))

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
                if val2 != 0 and GOAL_C[val2] == c and val1 > val2:
                    lc += 2

    cc = 0
    # Top-right corner (tile 3 at pos 3)
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        cc += 2
    # Bottom-left corner (tile 12 at pos 12)
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        cc += 2
    # Bottom-right corner (tile 15 at pos 15)
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        cc += 2

    base_h = md + lc * 6 + cc

    return int(base_h * 3.2)