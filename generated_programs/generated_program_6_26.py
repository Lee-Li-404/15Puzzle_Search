from fifteen_state_class import State

def heuristic(s: State) -> int:
    # Precompute Manhattan Distance lookup table for all (current_pos, tile_value) pairs
    # MD_TABLE[current_position][tile_value] stores the Manhattan distance
    # from current_position to tile_value's goal_position.
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
        if val != 0:  # Tile 0 is the blank, it doesn't contribute to MD.
            md += MD_TABLE[i][val]

    # Linear Conflicts (LC) calculation.
    # A linear conflict occurs when two tiles are in their goal row/column
    # but are in the wrong order relative to each other.
    lc = 0
    # Row conflicts
    for r in range(4):
        for c1 in range(4):
            val1 = tiles[r * 4 + c1]
            # Check if val1 is a non-blank tile and is in its goal row.
            if val1 == 0 or GOAL_R[val1] != r:
                continue
            for c2 in range(c1 + 1, 4):
                val2 = tiles[r * 4 + c2]
                # Check if val2 is a non-blank tile, also in the same goal row,
                # and in conflict (val1 should appear before val2 in the goal order but is after).
                if val2 != 0 and GOAL_R[val2] == r and val1 > val2:
                    lc += 1
    # Column conflicts
    for c in range(4):
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            # Check if val1 is a non-blank tile and is in its goal column.
            if val1 == 0 or GOAL_C[val1] != c:
                continue
            for r2 in range(r1 + 1, 4):
                val2 = tiles[r2 * 4 + c]
                # Check if val2 is a non-blank tile, also in the same goal column,
                # and in conflict (val1's goal row should be less than val2's goal row but is greater).
                if val2 != 0 and GOAL_C[val2] == c and GOAL_R[val1] > GOAL_R[val2]:
                    lc += 1

    # Corner Conflicts (CC) calculation.
    # Penalize specific corner tiles that are in their goal position
    # but are 'locked' by misaligned direct neighbors, making them hard to move out.
    cc = 0
    # Top-right corner (position 3, which is the goal for tile 3).
    # Conflict if tile 3 is in place, but tile 2 (left) or tile 7 (below) are not.
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        cc += 1
    # Bottom-left corner (position 12, which is the goal for tile 12).
    # Conflict if tile 12 is in place, but tile 8 (above) or tile 13 (right) are not.
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        cc += 1
    # Bottom-right corner (position 15, which is the goal for tile 15).
    # Conflict if tile 15 == 15 and (tiles[11] != 11 or tiles[14] != 14):
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        cc += 1

    # Weighting strategy:
    # This heuristic builds upon the best-performing predecessor (MD + 3.5 * LC + 0.5 * CC) * 3.3,
    # which achieved cost_ratio=1.737. Since this is well below the 1.80 bound,
    # we have room to increase the overall greediness of the heuristic to further reduce generated nodes.
    # We maintain the robust relative weights of MD, LC, and CC, but apply a slightly higher
    # overall multiplier. This uniform scaling should retain the balanced effectiveness of the
    # components while making the heuristic more aggressive in pruning the search space.

    conflict_weight_LC = 3.5
    conflict_weight_CC = 0.5
    overall_weight = 3.4  # Increased from 3.3 to 3.4 to leverage remaining cost_ratio headroom

    base_h = md + conflict_weight_LC * lc + conflict_weight_CC * cc

    return int(base_h * overall_weight)