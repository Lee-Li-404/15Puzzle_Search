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
                if val2 != 0 and GOAL_R[val2] == r and GOAL_C[val1] > GOAL_C[val2]:
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

    # The previous best heuristic (v1) used lc * 5 and a multiplier of 2.9.
    # The current best (score=0.0009) uses lc * 5 and 2.9 multiplier.
    # The heuristic_vr0 which scored 0.0009 used lc * 6 and 3.0 multiplier.
    # The heuristic_vr1 which scored 0.0010 used lc * 2 and 3.4 multiplier.
    # Let's try to increase the LC multiplier and the overall multiplier slightly
    # from the previous best, aiming to reduce generated nodes while staying within cost_ratio.
    # Previous best (v1) had cost 1.612. We have headroom.
    # Let's try lc * 6 and multiplier * 3.0, similar to vr0 but with better constants.
    # The MD_TABLE used in v1 and vr0 are identical. The GOAL_R and GOAL_C are also identical.
    # Let's combine the logic and tune parameters.
    # We will use the md + lc*6 + cc base and then multiply.
    # The previous best multiplier was 2.9. vr0 used 3.0.
    # Let's try a multiplier of 3.1 to be slightly more aggressive than vr0.
    # This is a greedy heuristic, so it doesn't need to be admissible.
    
    base_h = md + lc * 6 + cc
    
    # Increased overall weight to make the search more greedy.
    # This aims to reduce generated nodes further.
    return int(base_h * 3.1)
