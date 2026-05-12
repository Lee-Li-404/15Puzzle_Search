from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic evolves the best-performing previous version (score=0.0006) by further
    amplifying the penalties for difficult-to-resolve patterns and increasing the
    overall greedy weighting factor. The goal is to leverage the remaining headroom in the
    cost_ratio bound (<= 1.80) for more aggressive pruning of the A* search tree,
    thereby minimizing the number of unique nodes generated.

    The successful formula combining Manhattan Distance (MD), Linear Conflicts (LC),
    and Corner Conflicts (CC) is retained and made more aggressive:

    1.  Increased Linear Conflict Weight: The penalty multiplier for linear
        conflicts is increased from 5 to 6. This places an even higher penalty
        on tiles that are in their correct row/column but are inverted relative
        to their goal positions, as this is a very strong indicator of a
        difficult-to-resolve subproblem.

    2.  Increased Overall Weighting Factor: The final greedy weighting factor is
        incremented from 3.2 to 3.3. This small but significant increase makes
        the A* search more focused, further inflating the heuristic value to
        prioritize paths that appear closer to the goal, even at a slight risk
        to optimality.

    The heuristic is calculated as: `int((MD + LC * 6 + CC) * 3.3)`.
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
    # Increased from 3.2 to 3.3 to maximize node reduction.
    return int(base_h * 3.3)