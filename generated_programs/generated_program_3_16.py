from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic further refines the previous best-performing version (which achieved a score of 0.0006).
    The goal is to leverage any remaining headroom in the cost_ratio bound (<= 1.80)
    for even more aggressive pruning of the A* search tree, thereby minimizing the number
    of unique nodes generated.

    The successful formula combining Manhattan Distance (MD), Linear Conflicts (LC), and Corner Conflicts (CC) is retained:

    1.  Manhattan Distance (MD): Standard calculation.
    2.  Linear Conflict Weight: The penalty multiplier for linear conflicts remains at 6 (`lc * 6`).
        This has proven highly effective for difficult-to-resolve patterns.
    3.  Corner Conflicts (CC): Penalizes specific corner tiles if they are in their goal position
        but are 'blocking' adjacent tiles. Penalty remains at 2 per conflict.
    4.  Overall Weighting Factor: Incrementing from 3.4 to 3.45. This makes the A* search
        marginally more focused and greedy, further inflating the heuristic value to
        prioritize paths that appear closer to the goal. This small increment is intended
        to push generated nodes lower while remaining safely within the cost_ratio limit.

    The heuristic is calculated as: `int((MD + LC * 6 + CC) * 3.45)`.
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
    # Increased from 3.4 to 3.45 to maximize node reduction while attempting to stay within cost_ratio limits.
    return int(base_h * 3.45)