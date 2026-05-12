from fifteen_state_class import State
#   23 |      0 | 18 | 0.002378 |  0.002378 |   1.142857 |      nan |       nan
#[EVAL] avg_generated_ratio=0.00131486, max_cost_ratio=1.23529412
#1.15
def heuristic(s: State) -> int:
    if not hasattr(heuristic, "tbl"):
        # Define weights for each tile based on its goal row. 
        # Tiles in earlier rows get higher weights, encouraging progress.
        # Weights are empirically tuned to be aggressive but stay within cost bounds.
        weights = [0] + [155]*4 + [152]*4 + [149]*4 + [146]*3

        heuristic.tbl = tuple(
            tuple(
                0 if v == 0 else (abs((v >> 2) - (i >> 2)) + abs((v & 3) - (i & 3))) * weights[v]
                for v in range(16)
            )
            for i in range(16)
        )

    tiles = s.tiles
    H = heuristic.tbl
    h_val = 0

    # Calculate Weighted Manhattan Distance + Row-based Blocking Penalty
    for i, t in enumerate(tiles):
        if t:
            h_val += H[i][t]
            # Row-based Blocking Penalty: If a tile is not in its goal row
            # and its goal position in that row is occupied by another tile.
            if (t >> 2) != (i >> 2) and tiles[t] != 0:
                h_val += 22 # Penalty for blocking a tile in its target row

    # Linear Conflicts (LC)
    lc = 0

    # Row Conflicts
    for r in range(0, 16, 4):
        ridx = r >> 2
        t0 = tiles[r]; t1 = tiles[r+1]; t2 = tiles[r+2]; t3 = tiles[r+3]

        # Check all pairs for inversions within the same row, prioritizing tiles in earlier positions.
        if t0 and t1 and (t0 >> 2) == ridx and (t1 >> 2) == ridx and t0 > t1: lc += 1
        if t0 and t2 and (t0 >> 2) == ridx and (t2 >> 2) == ridx and t0 > t2: lc += 1
        if t0 and t3 and (t0 >> 2) == ridx and (t3 >> 2) == ridx and t0 > t3: lc += 1
        if t1 and t2 and (t1 >> 2) == ridx and (t2 >> 2) == ridx and t1 > t2: lc += 1
        if t1 and t3 and (t1 >> 2) == ridx and (t3 >> 2) == ridx and t1 > t3: lc += 1
        if t2 and t3 and (t2 >> 2) == ridx and (t3 >> 2) == ridx and t2 > t3: lc += 1

    # Column Conflicts
    for c in range(4):
        t0 = tiles[c]; t1 = tiles[c+4]; t2 = tiles[c+8]; t3 = tiles[c+12]

        # Check all pairs for inversions within the same column, prioritizing tiles in earlier positions.
        if t0 and t1 and (t0 & 3) == c and (t1 & 3) == c and t0 > t1: lc += 1
        if t0 and t2 and (t0 & 3) == c and (t2 & 3) == c and t0 > t2: lc += 1
        if t0 and t3 and (t0 & 3) == c and (t3 & 3) == c and t0 > t3: lc += 1
        if t1 and t2 and (t1 & 3) == c and (t2 & 3) == c and t1 > t2: lc += 1
        if t1 and t3 and (t1 & 3) == c and (t3 & 3) == c and t1 > t3: lc += 1
        if t2 and t3 and (t2 & 3) == c and (t3 & 3) == c and t2 > t3: lc += 1

    # Combine: Weighted MD (scaled ~1.46-1.55) + Row Blocking Penalty + LC * 420
    # The multiplier 420 for LC is aggressive, treating each conflict pair as ~4.2 moves.
    # This aims to significantly reduce node generation by penalizing linear conflicts heavily.
    return (h_val + lc * 420) // 100
