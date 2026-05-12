from fifteen_state_class import State

def heuristic(s: State) -> int:
    # This heuristic evolves the best-performing predecessor, which used the formula:
    # (MD + 3.5 * LC + 0.5 * CC) * 3.3
    # That version achieved a top score by increasing the overall weight from 3.2 to 3.3,
    # capitalizing on the cost_ratio headroom. This evolution continues that strategy
    # by pushing the overall multiplier further to 3.35, a small but aggressive step to
    # reduce the search space while staying within the cost_ratio limits.
    # It also slightly increases the corner conflict weight to better guide the search
    # away from specific, difficult-to-resolve "locked tile" configurations.

    # Precompute Manhattan Distance lookup table for all (current_pos, tile_value) pairs.
    MD_TABLE = tuple(
        tuple(
            abs((i // 4) - (val // 4)) + abs((i % 4) - (val % 4))
            for val in range(16)
        )
        for i in range(16)
    )

    # Precompute goal row and column for each tile value for efficiency.
    GOAL_R = tuple(val // 4 for val in range(16))
    GOAL_C = tuple(val % 4 for val in range(16))

    tiles = s.tiles

    # Manhattan Distance (MD) calculation using the precomputed table.
    md = 0
    for i, val in enumerate(tiles):
        if val != 0:
            md += MD_TABLE[i][val]

    # Linear Conflicts (LC) calculation.
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
                    lc += 1
    # Column conflicts
    for c in range(4):
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            if val1 == 0 or GOAL_C[val1] != c:
                continue
            for r2 in range(r1 + 1, 4):
                val2 = tiles[r2 * 4 + c]
                if val2 != 0 and GOAL_C[val2] == c and GOAL_R[val1] > GOAL_R[val2]:
                    lc += 1

    # Corner Conflicts (CC) calculation.
    cc = 0
    # Top-right corner (position 3, tile 3)
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        cc += 1
    # Bottom-left corner (position 12, tile 12)
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        cc += 1
    # Bottom-right corner (position 15, tile 15)
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        cc += 1

    # Carefully tuned weights based on iterative improvement.
    conflict_weight_LC = 3.5
    conflict_weight_CC = 0.6
    overall_weight = 3.35

    base_h = md + conflict_weight_LC * lc + conflict_weight_CC * cc

    return int(base_h * overall_weight)