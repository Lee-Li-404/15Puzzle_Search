from fifteen_state_class import State
#1.55

def heuristic(s: State) -> int:
    # Initialize static lookup table on first call
    if not hasattr(heuristic, "tbl"):
        # Precompute Manhattan distances. 
        # IMPORTANT: Column 0 is zeroed out because tiles[i]==0 (blank) contributes 0 cost.
        # This allows us to sum md without branching 'if val != 0'.
        tbl = []
        for i in range(16):
            row = []
            ir, ic = i // 4, i % 4
            for v in range(16):
                if v == 0:
                    row.append(0)
                else:
                    vr, vc = v // 4, v % 4
                    row.append(abs(ir - vr) + abs(ic - vc))
            tbl.append(tuple(row))
        heuristic.tbl = tuple(tbl)

    tiles = s.tiles
    tbl = heuristic.tbl
    lc = 0
    
    # 1. Manhattan Distance (Unrolled for O(1) speed)
    t0, t1, t2, t3 = tiles[0], tiles[1], tiles[2], tiles[3]
    t4, t5, t6, t7 = tiles[4], tiles[5], tiles[6], tiles[7]
    t8, t9, t10, t11 = tiles[8], tiles[9], tiles[10], tiles[11]
    t12, t13, t14, t15 = tiles[12], tiles[13], tiles[14], tiles[15]

    md = (tbl[0][t0] + tbl[1][t1] + tbl[2][t2] + tbl[3][t3] +
          tbl[4][t4] + tbl[5][t5] + tbl[6][t6] + tbl[7][t7] +
          tbl[8][t8] + tbl[9][t9] + tbl[10][t10] + tbl[11][t11] +
          tbl[12][t12] + tbl[13][t13] + tbl[14][t14] + tbl[15][t15])

    # 2. Row Linear Conflicts & Horizontal Swaps
    # Row 0
    c0, c1, c2, c3 = (t0 and t0 < 4), (t1 and t1 < 4), (t2 and t2 < 4), (t3 and t3 < 4)
    if c0:
        if c1 and t0 > t1: lc += 2
        if c2 and t0 > t2: lc += 2
        if c3 and t0 > t3: lc += 2
    if c1:
        if c2 and t1 > t2: lc += 2
        if c3 and t1 > t3: lc += 2
    if c2 and c3 and t2 > t3: lc += 2
    if t1 == 2 and t2 == 1: lc += 4
    if t2 == 3 and t3 == 2: lc += 4

    # Row 1
    c4, c5, c6, c7 = (t4 and 4 <= t4 < 8), (t5 and 4 <= t5 < 8), (t6 and 4 <= t6 < 8), (t7 and 4 <= t7 < 8)
    if c4:
        if c5 and t4 > t5: lc += 2
        if c6 and t4 > t6: lc += 2
        if c7 and t4 > t7: lc += 2
    if c5:
        if c6 and t5 > t6: lc += 2
        if c7 and t5 > t7: lc += 2
    if c6 and c7 and t6 > t7: lc += 2
    if t4 == 5 and t5 == 4: lc += 4
    if t5 == 6 and t6 == 5: lc += 4
    if t6 == 7 and t7 == 6: lc += 4

    # Row 2
    c8, c9, c10, c11 = (t8 and 8 <= t8 < 12), (t9 and 8 <= t9 < 12), (t10 and 8 <= t10 < 12), (t11 and 8 <= t11 < 12)
    if c8:
        if c9 and t8 > t9: lc += 2
        if c10 and t8 > t10: lc += 2
        if c11 and t8 > t11: lc += 2
    if c9:
        if c10 and t9 > t10: lc += 2
        if c11 and t9 > t11: lc += 2
    if c10 and c11 and t10 > t11: lc += 2
    if t8 == 9 and t9 == 8: lc += 4
    if t9 == 10 and t10 == 9: lc += 4
    if t10 == 11 and t11 == 10: lc += 4

    # Row 3
    c12, c13, c14, c15 = (t12 and t12 >= 12), (t13 and t13 >= 12), (t14 and t14 >= 12), (t15 and t15 >= 12)
    if c12:
        if c13 and t12 > t13: lc += 2
        if c14 and t12 > t14: lc += 2
        if c15 and t12 > t15: lc += 2
    if c13:
        if c14 and t13 > t14: lc += 2
        if c15 and t13 > t15: lc += 2
    if c14 and c15 and t14 > t15: lc += 2
    if t12 == 13 and t13 == 12: lc += 4
    if t13 == 14 and t14 == 13: lc += 4
    if t14 == 15 and t15 == 14: lc += 4

    # 3. Column Linear Conflicts & Vertical Swaps
    # Col 0
    c0, c4, c8, c12 = (t0 and (t0 & 3) == 0), (t4 and (t4 & 3) == 0), (t8 and (t8 & 3) == 0), (t12 and (t12 & 3) == 0)
    if c0:
        if c4 and t0 > t4: lc += 2
        if c8 and t0 > t8: lc += 2
        if c12 and t0 > t12: lc += 2
    if c4:
        if c8 and t4 > t8: lc += 2
        if c12 and t4 > t12: lc += 2
    if c8 and c12 and t8 > t12: lc += 2
    if t4 == 8 and t8 == 4: lc += 4
    if t8 == 12 and t12 == 8: lc += 4

    # Col 1
    c1, c5, c9, c13 = (t1 and (t1 & 3) == 1), (t5 and (t5 & 3) == 1), (t9 and (t9 & 3) == 1), (t13 and (t13 & 3) == 1)
    if c1:
        if c5 and t1 > t5: lc += 2
        if c9 and t1 > t9: lc += 2
        if c13 and t1 > t13: lc += 2
    if c5:
        if c9 and t5 > t9: lc += 2
        if c13 and t5 > t13: lc += 2
    if c9 and c13 and t9 > t13: lc += 2
    if t1 == 5 and t5 == 1: lc += 4
    if t5 == 9 and t9 == 5: lc += 4
    if t9 == 13 and t13 == 9: lc += 4

    # Col 2
    c2, c6, c10, c14 = (t2 and (t2 & 3) == 2), (t6 and (t6 & 3) == 2), (t10 and (t10 & 3) == 2), (t14 and (t14 & 3) == 2)
    if c2:
        if c6 and t2 > t6: lc += 2
        if c10 and t2 > t10: lc += 2
        if c14 and t2 > t14: lc += 2
    if c6:
        if c10 and t6 > t10: lc += 2
        if c14 and t6 > t14: lc += 2
    if c10 and c14 and t10 > t14: lc += 2
    if t2 == 6 and t6 == 2: lc += 4
    if t6 == 10 and t10 == 6: lc += 4
    if t10 == 14 and t14 == 10: lc += 4

    # Col 3
    c3, c7, c11, c15 = (t3 and (t3 & 3) == 3), (t7 and (t7 & 3) == 3), (t11 and (t11 & 3) == 3), (t15 and (t15 & 3) == 3)
    if c3:
        if c7 and t3 > t7: lc += 2
        if c11 and t3 > t11: lc += 2
        if c15 and t3 > t15: lc += 2
    if c7:
        if c11 and t7 > t11: lc += 2
        if c15 and t7 > t15: lc += 2
    if c11 and c15 and t11 > t15: lc += 2
    if t3 == 7 and t7 == 3: lc += 4
    if t7 == 11 and t11 == 7: lc += 4
    if t11 == 15 and t15 == 11: lc += 4

    # 4. Corner Penalties
    # Penalize locked corners with wrong tiles
    corner = 0
    if t0 and t1 == 1 and t4 == 4: corner += 5
    if t3 != 3 and t2 == 2 and t7 == 7: corner += 5
    if t12 != 12 and t8 == 8 and t13 == 13: corner += 5
    if t15 != 15 and t11 == 11 and t14 == 14: corner += 5

    # Weight tuned to 2.58 to minimize nodes while keeping cost_ratio < 1.55
    return int((md + lc + corner) * 2.58)