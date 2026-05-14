from fifteen_state_class import State
#1.65
def heuristic(s: State) -> int:
    if not hasattr(heuristic, "costs"):
        # Precompute cost table: Weighted Manhattan + Quadratic Penalty
        # Weights prioritize solving top rows first (Greedy approach).
        # Row 0 (1-4): 27 (2.7x), Row 1 (5-8): 17 (1.7x), Row 2 (9-12): 12 (1.2x), Row 3: 10 (1.0x)
        W = [0, 
             27, 27, 27, 27, 
             17, 17, 17, 17, 
             12, 12, 12, 12, 
             10, 10, 10]
        
        # Quadratic coefficient (0.4 * d^2) to punish far-flung tiles
        K_QUAD = 4

        costs = [[0] * 16 for _ in range(16)]
        for val in range(16):
            if val == 0: continue
            goal_r, goal_c = val >> 2, val & 3
            w = W[val]
            for pos in range(16):
                r, c = pos >> 2, pos & 3
                md = abs(r - goal_r) + abs(c - goal_c)
                costs[pos][val] = w * md + (md * md * K_QUAD)
        
        heuristic.costs = tuple(tuple(row) for row in costs)

    tiles = s.tiles
    h_val = 0
    tbl = heuristic.costs

    # 1. Sum Precomputed Costs (O(16))
    for i, t in enumerate(tiles):
        if t:
            h_val += tbl[i][t]

    # 2. Linear Conflicts (O(1) unrolled checks)
    # Penalty = 125 units (approx 12.5 moves). Higher penalty prunes nodes aggressively.
    lc = 0
    
    # Row Conflicts
    for r in range(4):
        b = r << 2
        t0, t1, t2, t3 = tiles[b], tiles[b+1], tiles[b+2], tiles[b+3]
        # Check if tile is non-zero AND belongs to this row
        in0 = t0 and (t0 >> 2) == r
        in1 = t1 and (t1 >> 2) == r
        in2 = t2 and (t2 >> 2) == r
        in3 = t3 and (t3 >> 2) == r
        
        if in0:
            if in1 and t0 > t1: lc += 1
            if in2 and t0 > t2: lc += 1
            if in3 and t0 > t3: lc += 1
        if in1:
            if in2 and t1 > t2: lc += 1
            if in3 and t1 > t3: lc += 1
        if in2 and in3 and t2 > t3: lc += 1

    # Column Conflicts
    for c in range(4):
        t0, t1, t2, t3 = tiles[c], tiles[c+4], tiles[c+8], tiles[c+12]
        # Check if tile is non-zero AND belongs to this column
        in0 = t0 and (t0 & 3) == c
        in1 = t1 and (t1 & 3) == c
        in2 = t2 and (t2 & 3) == c
        in3 = t3 and (t3 & 3) == c
        
        if in0:
            if in1 and t0 > t1: lc += 1
            if in2 and t0 > t2: lc += 1
            if in3 and t0 > t3: lc += 1
        if in1:
            if in2 and t1 > t2: lc += 1
            if in3 and t1 > t3: lc += 1
        if in2 and in3 and t2 > t3: lc += 1

    h_val += lc * 125

    # Return scaled result
    return (h_val + 5) // 10