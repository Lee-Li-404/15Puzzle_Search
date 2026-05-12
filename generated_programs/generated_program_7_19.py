from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic combines Manhattan Distance (MD), Linear Conflicts (LC), and Corner Conflicts (CC)
    with aggressive weighting to reduce the number of generated nodes while aiming to stay
    within the cost_ratio <= 1.80 bound.

    The strategy is to increase the penalty for linear and corner conflicts, as these often
    represent harder-to-resolve states. A higher overall multiplier is used to make the A*
    search more greedy, pruning more branches.
    
    Based on previous successful heuristics, `lc * 6` is a good starting point for linear conflicts.
    The `cc` term adds specific penalties for tricky corner configurations.
    A final multiplier is used to further inflate the heuristic value.
    
    Targeting a multiplier slightly higher than the best previous scores (e.g., 3.1 or 3.2) 
    to reduce generated nodes, given the cost_ratio headroom.
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

    # Base heuristic combining Manhattan Distance, heavily weighted Linear Conflicts, and Corner Conflicts.
    # lc * 6 is retained from previous successful attempts.
    base_h = md + lc * 6 + cc

    # Apply a higher overall multiplier to make the heuristic more greedy.
    # The previous best score (0.0009) used a multiplier of 2.9 or 3.0. 
    # Given a cost_ratio headroom (1.612 vs 1.80), increasing to 3.1 or 3.2 
    # might further reduce generated nodes.
    # Let's try 3.15, a value between the best known and slightly more aggressive.
    return int(base_h * 3.15)
