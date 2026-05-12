from fifteen_state_class import State
#    set cost bound during training: 1.25
def heuristic(s: State) -> int:
    if not hasattr(heuristic, "lookup"):
        # Precompute weights and tables on first call
        # Weights are calibrated to prioritize solving Corner and Edge tiles first (hard constraints).
        # The average weight is pushed to ~1.68 to aggressively reduce generated nodes
        # while maintaining the cost ratio bound of 1.25.
        W_CORNER = 1.85
        W_EDGE = 1.70
        W_CENTER = 1.55
        LC_COST = 3.4  # Linear Conflict cost (2.0 * ~1.7 weight)

        # Assign weights to tiles based on their goal position
        # 0 is Blank, 3,12,15 are Corners, etc.
        weights = [0.0] * 16
        for v in range(1, 16):
            r, c = v >> 2, v & 3
            if (r == 0 or r == 3) and (c == 0 or c == 3):
                weights[v] = W_CORNER
            elif r == 0 or r == 3 or c == 0 or c == 3:
                weights[v] = W_EDGE
            else:
                weights[v] = W_CENTER

        # Flattened Weighted Manhattan Table: lookup[(current_pos << 4) | tile_val]
        tbl = [0.0] * 256
        for pos in range(16):
            r_p, c_p = pos >> 2, pos & 3
            for v in range(16):
                if v == 0: continue
                r_v, c_v = v >> 2, v & 3
                dist = abs(r_p - r_v) + abs(c_p - c_v)
                tbl[(pos << 4) | v] = dist * weights[v]
        
        heuristic.lookup = tuple(tbl)
        heuristic.LC = LC_COST

    tiles = s.tiles
    lookup = heuristic.lookup
    lc = heuristic.LC
    h = 0.0

    # 1. Weighted Manhattan Distance
    # Using flattened lookup for speed: O(16)
    for i, v in enumerate(tiles):
        if v:
            h += lookup[(i << 4) | v]

    # 2. Linear Conflicts (Rows)
    # Check for inversions among tiles that belong to the same row.
    for r in range(4):
        base = r << 2
        t0, t1, t2, t3 = tiles[base], tiles[base+1], tiles[base+2], tiles[base+3]
        
        # Check if tile belongs to this row (val >> 2 == r) and is not blank
        in0 = t0 and (t0 >> 2) == r
        in1 = t1 and (t1 >> 2) == r
        in2 = t2 and (t2 >> 2) == r
        in3 = t3 and (t3 >> 2) == r
        
        # Add penalty for every pair in conflict
        if in0:
            if in1 and t0 > t1: h += lc
            if in2 and t0 > t2: h += lc
            if in3 and t0 > t3: h += lc
        if in1:
            if in2 and t1 > t2: h += lc
            if in3 and t1 > t3: h += lc
        if in2:
            if in3 and t2 > t3: h += lc

    # 3. Linear Conflicts (Columns)
    for c in range(4):
        t0, t1, t2, t3 = tiles[c], tiles[c+4], tiles[c+8], tiles[c+12]
        
        # Check if tile belongs to this column (val & 3 == c) and is not blank
        in0 = t0 and (t0 & 3) == c
        in1 = t1 and (t1 & 3) == c
        in2 = t2 and (t2 & 3) == c
        in3 = t3 and (t3 & 3) == c
        
        if in0:
            if in1 and t0 > t1: h += lc
            if in2 and t0 > t2: h += lc
            if in3 and t0 > t3: h += lc
        if in1:
            if in2 and t1 > t2: h += lc
            if in3 and t1 > t3: h += lc
        if in2:
            if in3 and t2 > t3: h += lc

    return int(h)