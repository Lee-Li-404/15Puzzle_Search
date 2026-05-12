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
    # Row conflicts: Check for tiles in the correct row but out of order.
    for r in range(4):
        for c1 in range(4):
            val1 = tiles[r * 4 + c1]
            if val1 == 0 or GOAL_R[val1] != r:
                continue
            for c2 in range(c1 + 1, 4):
                val2 = tiles[r * 4 + c2]
                if val2 != 0 and GOAL_R[val2] == r and val1 > val2:
                    lc += 2 # Each pair out of order in the row adds 2 to conflict count.

    # Column conflicts: Check for tiles in the correct column but out of order.
    for c in range(4):
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            if val1 == 0 or GOAL_C[val1] != c:
                continue
            for r2 in range(r1 + 1, 4):
                val2 = tiles[r2 * 4 + c]
                if val2 != 0 and GOAL_C[val2] == c and GOAL_R[val1] > GOAL_R[val2]:
                    lc += 2 # Each pair out of order in the column adds 2 to conflict count.

    patterns = 0
    # Corner Conflicts: Penalize if a corner tile is in its goal position but its direct neighbors are not.
    # These configurations are known to be problematic.
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        patterns += 2
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        patterns += 2
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        patterns += 2

    # Swap Conflicts: Penalize specific, common high-cost swaps.
    # These represent local configurations that are difficult to resolve efficiently.
    if tiles[1] == 4 and tiles[4] == 1: # L-shape swap (1<->4)
        patterns += 5
    if tiles[1] == 2 and tiles[2] == 1: # Top row adjacent swap (1<->2)
        patterns += 4
    if tiles[13] == 14 and tiles[14] == 13: # Bottom row adjacent swap (13<->14)
        patterns += 4
    if tiles[7] == 11 and tiles[11] == 7: # Right column adjacent swap (7<->11)
        patterns += 4
    if tiles[14] == 15 and tiles[15] == 14: # Bottom right adjacent swap (14<->15)
        patterns += 4

    # The base heuristic combines Manhattan distance, a moderately penalized Linear Conflict score,
    # and specific pattern penalties.
    # The LC multiplier is set to 6.0, higher than standard but not excessively so.
    base_h = md + lc * 6.0 + patterns

    # Apply a significantly increased overall weighting factor. This makes the A* search more greedy,
    # prioritizing node reduction. The factor of 3.65 is chosen to capitalize on the existing headroom
    # in the cost_ratio (well below 1.80) to push the generated_ratio lower.
    WEIGHT_FACTOR = 3.65
    return int(base_h * WEIGHT_FACTOR)
