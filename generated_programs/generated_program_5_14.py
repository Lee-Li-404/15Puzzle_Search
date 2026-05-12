from fifteen_state_class import State

def heuristic(s: State) -> int:
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
        row_vals = []
        for c in range(4):
            val = tiles[r * 4 + c]
            if val != 0 and GOAL_R[val] == r:
                row_vals.append(val)
        for i in range(len(row_vals)):
            for j in range(i + 1, len(row_vals)):
                if row_vals[i] > row_vals[j]:
                    lc += 2

    # Column conflicts
    for c in range(4):
        col_vals = []
        for r in range(4):
            val = tiles[r * 4 + c]
            if val != 0 and GOAL_C[val] == c:
                col_vals.append(val)
        for i in range(len(col_vals)):
            for j in range(i + 1, len(col_vals)):
                if GOAL_R[col_vals[i]] > GOAL_R[col_vals[j]]:
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

    # Base heuristic with an increased penalty for linear conflicts.
    base_h = md + lc * 4 + cc

    # Apply a high weight to make the search more greedy.
    return int(base_h * 3.0)
