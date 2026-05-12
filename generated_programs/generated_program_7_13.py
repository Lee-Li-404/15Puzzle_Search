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

    # Increase the multiplier for linear conflicts to 5.0, and the overall greedy weight to 2.9.
    # This aims to reduce generated nodes further while staying within cost_ratio bounds.
    # The values are chosen based on the successful strategy of heuristic_v1 and heuristic_vr2.
    return int((md + lc * 5.0) * 2.9)
