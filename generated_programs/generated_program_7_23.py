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
        if val != 0: # Blank tile (0) does not contribute to Manhattan distance
            md += MD_TABLE[i][val]

    lc = 0
    # Row conflicts: two tiles in their goal row but swapped order
    for r in range(4):
        for c1 in range(4):
            val1 = tiles[r * 4 + c1]
            if val1 == 0 or GOAL_R[val1] != r:
                continue
            for c2 in range(c1 + 1, 4): # Check tiles to the right
                val2 = tiles[r * 4 + c2]
                if val2 != 0 and GOAL_R[val2] == r and val1 > val2:
                    lc += 2 # Add 2 for each linear conflict, as per common practice

    # Column conflicts: two tiles in their goal column but swapped order
    for c in range(4):
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            if val1 == 0 or GOAL_C[val1] != c:
                continue
            for r2 in range(r1 + 1, 4): # Check tiles below
                val2 = tiles[r2 * 4 + c]
                if val2 != 0 and GOAL_C[val2] == c and GOAL_R[val1] > GOAL_R[val2]: # Compare goal rows for column conflicts
                    lc += 2

    cc = 0
    # Corner Conflicts: A tile in its goal corner position, but its required neighbors are not in place.
    # This implies a "stuck" corner requiring extra moves.
    # Top-right corner (index 3, goal tile 3)
    if tiles[3] == 3: 
        if tiles[2] != 2 or tiles[7] != 7:
            cc += 2
    # Bottom-left corner (index 12, goal tile 12)
    if tiles[12] == 12:
        if tiles[8] != 8 or tiles[13] != 13:
            cc += 2
    # Bottom-right corner (index 15, goal tile 15)
    if tiles[15] == 15:
        if tiles[11] != 11 or tiles[14] != 14:
            cc += 2

    # Adjusted weights:
    # LC_MULTIPLIER is reduced from 5 to 3 (compared to heuristic_prev0)
    # OVERALL_WEIGHT is slightly increased from 2.9 to 3.0 (compared to heuristic_prev0)
    # This aims to balance the high impact of linear conflicts while retaining corner conflict detection
    # and leveraging the available cost_ratio headroom to reduce generated nodes.
    LC_MULTIPLIER = 3
    OVERALL_WEIGHT = 3.0

    base_h = md + lc * LC_MULTIPLIER + cc

    return int(base_h * OVERALL_WEIGHT)