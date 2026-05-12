from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic pushes the boundaries of greediness based on previous successful
    iterations, which showed that high penalties for linear conflicts combined with
    a large overall multiplier effectively reduce the number of generated nodes.
    Given that prior best versions had a cost_ratio well below the 1.80 limit,
    this version becomes even more aggressive.

    Key Changes:
    1. Increased Linear Conflict (LC) Weight: The weight for the linear conflict
       term is increased from 12 (in the previous best) to 13. This further
       penalizes states with tiles in their correct row/column but in the wrong
       order, steering the search away from these known difficult configurations
       more forcefully.

    2. Increased Greedy Multiplier: The final multiplier is nudged up from 3.6
       to 3.7. This inflates all heuristic values slightly more, making the
       A* search greedier overall. It aims to prune more branches of the search
       tree, capitalizing on the available headroom in the cost_ratio.

    The strategy is to combine a highly targeted penalty (LC weight) with a
    broad-stroke inflation (greedy multiplier) to achieve a new minimum for
    the generated_ratio.
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

    md = 0  # Manhattan Distance
    for i, val in enumerate(tiles):
        if val != 0:
            md += MD_TABLE[i][val]

    lc = 0  # Linear Conflicts
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

    cc = 0  # Corner Conflicts
    # Top-right corner (tile 3 at index 3)
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        cc += 2
    # Bottom-left corner (tile 12 at index 12)
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        cc += 2
    # Bottom-right corner (tile 15 at index 15)
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        cc += 2

    # Incrementally increase the linear conflict penalty from 12 to 13.
    base_h = md + lc * 13 + cc

    # Nudge the overall greedy multiplier from 3.6 to 3.7 to further
    # reduce generated nodes, using the available cost_ratio headroom.
    return int(base_h * 3.7)