from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic evolves the previous best-performing versions by further
    increasing the penalty for linear conflicts, which are a key indicator of
    a difficult puzzle state. The core idea is that resolving a linear conflict
    requires moving tiles out of their goal row/column and back in, which is
    expensive. By penalizing this more heavily, we guide the A* search away
    from these states more forcefully.

    Changes from the previous best:
    1.  Increased Linear Conflict Multiplier: The weight for the linear
        conflict term (lc) has been increased from 6 to 7. This is a direct
        continuation of the trend that has yielded the best scores, where
        incrementally increasing the `lc` weight improved performance.
        The base heuristic is now `md + lc * 7 + cc`.

    2.  Retained Greedy Multiplier: The overall greedy multiplier is kept at
        3.6. This value has proven effective in balancing search greediness
        (reducing generated nodes) with solution quality (keeping cost_ratio
        low). Increasing the `lc` weight is a more targeted way to improve
        the heuristic's power than simply increasing the final multiplier.

    This combination aims to achieve a new best score by further reducing the
    `generated_ratio`, leveraging the headroom available in the `cost_ratio`
    constraint.
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
    # Check if corner tiles are in place but are blocking other tiles.
    # Top-right corner (tile 3 at index 3)
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        cc += 2
    # Bottom-left corner (tile 12 at index 12)
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        cc += 2
    # Bottom-right corner (tile 15 at index 15)
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        cc += 2

    # Increasing the linear conflict penalty from 6 to 7. This term has proven
    # to be the most impactful for pruning the search tree.
    base_h = md + lc * 7 + cc

    # The overall greedy multiplier is maintained at 3.6, a value that has
    # consistently provided a good balance of greediness and solution quality.
    return int(base_h * 3.6)