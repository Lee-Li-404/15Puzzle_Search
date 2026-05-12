from fifteen_state_class import State

def heuristic(s: State) -> int:
    MD_TABLE = (
        (0, 1, 2, 3, 1, 2, 3, 4, 2, 3, 4, 5, 3, 4, 5, 6),
        (1, 0, 1, 2, 2, 1, 2, 3, 3, 2, 3, 4, 4, 3, 4, 5),
        (2, 1, 0, 1, 3, 2, 1, 2, 4, 3, 2, 3, 5, 4, 3, 4),
        (3, 2, 1, 0, 4, 3, 2, 1, 5, 4, 3, 2, 6, 5, 4, 3),
        (1, 2, 3, 4, 0, 1, 2, 3, 3, 4, 5, 6, 4, 5, 6, 7),
        (2, 1, 2, 3, 1, 0, 1, 2, 4, 3, 4, 5, 5, 4, 5, 6),
        (3, 2, 1, 2, 2, 1, 0, 1, 5, 4, 3, 4, 6, 5, 4, 5),
        (4, 3, 2, 1, 3, 2, 1, 0, 6, 5, 4, 3, 7, 6, 5, 4),
        (2, 3, 4, 5, 3, 4, 5, 6, 0, 1, 2, 3, 1, 2, 3, 4),
        (3, 2, 3, 4, 4, 3, 4, 5, 1, 0, 1, 2, 2, 1, 2, 3),
        (4, 3, 2, 3, 5, 4, 3, 4, 2, 1, 0, 1, 3, 2, 1, 2),
        (5, 4, 3, 2, 6, 5, 4, 3, 3, 2, 1, 0, 4, 3, 2, 1),
        (3, 4, 5, 6, 4, 5, 6, 7, 1, 2, 3, 4, 0, 1, 2, 3),
        (4, 3, 4, 5, 5, 4, 5, 6, 2, 1, 2, 3, 1, 0, 1, 2),
        (5, 4, 3, 4, 6, 5, 4, 5, 3, 2, 1, 2, 2, 1, 0, 1),
        (6, 5, 4, 3, 7, 6, 5, 4, 4, 3, 2, 1, 3, 2, 1, 0)
    )
    GOAL_R = (0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3)
    GOAL_C = (0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3)

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
    # Top-right corner (tile 3)
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        cc += 2
    # Bottom-left corner (tile 12)
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        cc += 2
    # Bottom-right corner (tile 15)
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        cc += 2

    # Base heuristic combining MD, LC, and CC.
    # The previous best (v1) used lc * 5. The current best (vr1) used lc * 6.
    # Let's stick with lc * 6 for significant linear conflict penalty.
    base_h = md + lc * 6 + cc

    # Applying a multiplier for greediness.
    # v1 used 2.9, vr0 used 3.4, vr1 used 3.0.
    # The cost_ratio for v1 was 1.612, vr1 was 1.612. Both achieved score 0.0009.
    # vr0 had score 0.0010 with cost 1.680 and generated 0.001.
    # heuristic_prev0 had score 0.0012, cost 1.680, generated 0.001.
    # heuristic_prev1 had score 0.0018.
    # Since v1 and vr1 achieved the best score with cost 1.612, and the limit is 1.80,
    # there's room to increase greediness (multiplier) to potentially lower generated nodes.
    # Let's try a multiplier of 3.2, slightly higher than vr1's 3.0, to see if it further
    # reduces generated nodes while staying within the cost bound.
    # This is a greedy heuristic, so admissibility is not a concern.
    return int(base_h * 3.2)
