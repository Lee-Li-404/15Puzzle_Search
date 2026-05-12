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
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        patterns += 2
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        patterns += 2
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        patterns += 2

    # Swap Conflicts: Penalize specific, high-cost swaps extra.
    # These penalties are slightly increased from the previous best version
    # to further prune the search space for these known problematic configurations.
    # Top-left "L" shape swap (increased from 5 to 6).
    if tiles[1] == 4 and tiles[4] == 1:
        patterns += 6
    # Top row swap (increased from 4 to 5).
    if tiles[1] == 2 and tiles[2] == 1:
        patterns += 5
    # Last row swap (increased from 4 to 5).
    if tiles[13] == 14 and tiles[14] == 13:
        patterns += 5
    # Right column swap (increased from 4 to 5).
    if tiles[7] == 11 and tiles[11] == 7:
        patterns += 5

    # The base heuristic combines MD, heavily weighted LC, and pattern penalties.
    # Linear conflicts are weighted by 6, a factor found effective for strong pruning.
    base_h = md + lc * 6 + patterns

    # Final overall greedy multiplier. This factor is kept at 3.65 based on previous
    # experiments where a slightly higher global weight led to a worse generated_ratio,
    # even with the same cost_ratio. The current improvements are focused on specific
    # pattern penalties for more targeted pruning.
    WEIGHT_FACTOR = 3.65
    return int(base_h * WEIGHT_FACTOR)