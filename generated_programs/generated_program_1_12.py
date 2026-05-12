from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic improves upon the previous best model by being more
    aggressive, leveraging the significant headroom in the cost_ratio (1.612 vs 1.80).
    The goal is to drastically reduce the number of generated nodes.

    Key enhancements:
    1.  Increased Linear Conflict Weight: The multiplier for linear conflicts (lc)
        is boosted from 5 to 6. This amplifies the penalty for the most
        informative bad patterns, forcing the search to resolve them more directly.

    2.  Increased Overall Weighting Factor: The final greedy multiplier is raised
        from 2.9 to 3.1. This inflates the entire heuristic value, making the
        A* search greedier and pruning more of the search space.

    3.  Added Pattern Detection: A new penalty is added for a specific difficult
        pattern near the top-left corner: if tiles 1 and 4 are swapped.
        This is a common and costly local minimum to resolve.
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
                if val2 != 0 and GOAL_C[val2] == c and GOAL_R[val1] > GOAL_R[val2]:
                    lc += 2

    cc = 0
    # Original Corner Conflicts
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        cc += 2
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        cc += 2
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        cc += 2

    # New Pattern: Swapped tiles 1 and 4 near top-left corner
    if tiles[1] == 4 and tiles[4] == 1:
        cc += 4

    # The base heuristic now has a stronger weight for linear conflicts (lc * 6).
    base_h = md + lc * 6 + cc

    # The overall weight is increased to make the search even greedier.
    return int(base_h * 3.1)