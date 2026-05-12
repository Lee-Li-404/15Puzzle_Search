from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic evolves the best-performing previous versions by incorporating a
    "Last Moves" (LM) penalty. This new component identifies tiles that are already
    in their goal positions within the top row or left-most column, but which
    obstruct the blank tile from reaching its home at the top-left corner.

    The heuristic builds upon the successful combination of Manhattan Distance (MD),
    Linear Conflicts (LC), and Corner Conflicts (CC):

    1.  Manhattan Distance (MD): The standard base, pre-calculated for efficiency.

    2.  Aggressive Linear Conflict Weight: Retains the highly effective multiplier of 6
        for linear conflicts (`lc * 6`), which strongly penalizes tiles in the
        correct row/column but in the wrong order.

    3.  Corner Conflicts (CC): Keeps the proven penalty of 2 for each corner tile
        (3, 12, 15) that is in its goal position but blocks adjacent tiles.

    4.  NEW Last Moves Penalty (LM): If the blank tile is not in its goal row/column,
        a penalty of 2 is added for each tile correctly placed in that goal row/column,
        as these tiles must be moved out of the way.

    5.  Calibrated Overall Weight: The final greedy weighting factor is set to 3.4.
        This is a slight reduction from the previous best (3.45) to compensate for the
        addition of the LM penalty, ensuring the heuristic remains aggressive in
        pruning nodes while staying safely within the cost_ratio <= 1.80 bound.

    The final formula is: `int((MD + LC * 6 + CC + LM) * 3.4)`.
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
    blank_idx = -1
    for i, val in enumerate(tiles):
        if val != 0:
            md += MD_TABLE[i][val]
        else:
            blank_idx = i

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
    # Top-right corner (tile 3)
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        cc += 2
    # Bottom-left corner (tile 12)
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        cc += 2
    # Bottom-right corner (tile 15)
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        cc += 2

    lm = 0
    blank_r, blank_c = divmod(blank_idx, 4)
    # Penalty if blank is not in goal row (0) and a tile is blocking that row
    if blank_r != 0:
        if tiles[1] == 1: lm += 2
        if tiles[2] == 2: lm += 2
        if tiles[3] == 3: lm += 2
    # Penalty if blank is not in goal column (0) and a tile is blocking that column
    if blank_c != 0:
        if tiles[4] == 4: lm += 2
        if tiles[8] == 8: lm += 2
        if tiles[12] == 12: lm += 2

    base_h = md + lc * 6 + cc + lm
    return int(base_h * 3.4)