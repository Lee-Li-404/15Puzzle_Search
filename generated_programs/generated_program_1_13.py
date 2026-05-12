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
        if val != 0: # Ignore the blank tile for Manhattan distance
            md += MD_TABLE[i][val]

    lc = 0
    # Row conflicts
    for r in range(4):
        # Check for conflicts within this row among tiles that belong in this row.
        # A conflict exists if two tiles are in their goal row but are reversed
        # in order relative to their goal columns.
        for c1 in range(4):
            val1 = tiles[r * 4 + c1]
            if val1 == 0 or GOAL_R[val1] != r:
                continue
            for c2 in range(c1 + 1, 4):
                val2 = tiles[r * 4 + c2]
                if val2 != 0 and GOAL_R[val2] == r and val1 > val2:
                    lc += 2 # Add 2 for each conflict

    # Column conflicts
    for c in range(4):
        # Check for conflicts within this column among tiles that belong in this column.
        # A conflict exists if two tiles are in their goal column but are reversed
        # in order relative to their goal rows.
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            if val1 == 0 or GOAL_C[val1] != c:
                continue
            for r2 in range(r1 + 1, 4):
                val2 = tiles[r2 * 4 + c]
                if val2 != 0 and GOAL_C[val2] == c and GOAL_R[val1] > GOAL_R[val2]:
                    lc += 2 # Add 2 for each conflict

    cc = 0
    # Corner Conflicts: specific patterns that are hard to resolve.
    # Top-right corner (tile 3): if tile 3 is in place, but its neighbors (2, 7) are not correct.
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        cc += 2
    # Bottom-left corner (tile 12): if tile 12 is in place, but its neighbors (8, 13) are not correct.
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        cc += 2
    # Bottom-right corner (tile 15): if tile 15 is in place, but its neighbors (11, 14) are not correct.
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        cc += 2

    # Specific "L" pattern conflict near top-left: tiles 1 and 4 are swapped.
    # This is often a tough local minimum, and a dedicated penalty can help.
    if tiles[1] == 4 and tiles[4] == 1:
        cc += 4

    # The base heuristic combines Manhattan distance, linear conflicts (weighted x6),
    # and corner conflict penalties.
    base_h = md + lc * 6 + cc

    # Apply a strong overall weighting factor to make the A* search very greedy.
    # This leverages the significant headroom in the previous cost_ratio (1.612 vs 1.80 limit)
    # to drastically reduce the number of unique nodes generated.
    # The factor 3.45 is chosen to push the cost_ratio closer to the limit while maximizing node reduction.
    WEIGHT_FACTOR = 3.45
    return int(base_h * WEIGHT_FACTOR)