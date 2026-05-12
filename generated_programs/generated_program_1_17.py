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

    patterns = 0
    # Corner Conflicts: A corner tile is in place, blocking its neighbors.
    # These penalties are kept moderate as they proved effective in previous iterations.
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        patterns += 2
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        patterns += 2
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        patterns += 2

    # Swap Conflicts: Penalize specific, high-cost swaps extra.
    # The penalties for these critical patterns are retained from a high-performing previous version.
    # Top-left "L" shape swap.
    if tiles[1] == 4 and tiles[4] == 1:
        patterns += 5
    # Top row swap.
    if tiles[1] == 2 and tiles[2] == 1:
        patterns += 4
    # Last row swap.
    if tiles[13] == 14 and tiles[14] == 13:
        patterns += 4
    # Right column swap.
    if tiles[7] == 11 and tiles[11] == 7:
        patterns += 4

    # The base heuristic combines MD, heavily weighted LC, and pattern penalties.
    # Linear conflicts are weighted by 6, a factor found effective for strong pruning.
    base_h = md + lc * 6 + patterns

    # Final overall greedy multiplier. Building on the previous best (3.65), this version
    # increases the `WEIGHT_FACTOR` to 3.75. This is a targeted, conservative increase
    # to further reduce generated nodes, leveraging observed headroom in the cost_ratio
    # without making the heuristic too aggressive and exceeding the 1.80 bound.
    WEIGHT_FACTOR = 3.75
    return int(base_h * WEIGHT_FACTOR)