from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic builds upon the most successful prior versions by continuing the
    proven strategy of aggressively penalizing linear conflicts (LC).
    The core idea is that states with many linear conflicts require significantly
    more moves to resolve than their Manhattan distance alone would suggest.

    Key evolution from the previous best heuristic (`md + lc * 8 + cc`):
    1.  Increased Linear Conflict Weight: The multiplier for the linear conflict
        term is incremented from 8 to 9. This makes the heuristic even more
        sensitive to these difficult-to-resolve tile arrangements, guiding the
        A* search to prune these branches more aggressively.

    2.  Maintained Greedy Multiplier: The overall greedy multiplier is kept at 3.6.
        This value has demonstrated a strong balance between reducing the search
        space (generated nodes) and maintaining an acceptable solution quality
        (cost_ratio). The primary tuning is focused on the more nuanced LC term.

    This targeted adjustment aims to further reduce the `generated_ratio` by leveraging
    the remaining headroom in the `cost_ratio`, following the clear trend of
    performance improvements from increasing the LC penalty.
    """
    # Precompute goal positions for Manhattan distance and linear conflicts
    # MD_TABLE[current_idx][tile_value] = manhattan_distance
    MD_TABLE = tuple(
        tuple(
            abs((i // 4) - (val // 4)) + abs((i % 4) - (val % 4))
            for val in range(16)
        )
        for i in range(16)
    )
    # GOAL_R[tile_value] = goal_row
    GOAL_R = tuple(val // 4 for val in range(16))
    # GOAL_C[tile_value] = goal_col
    GOAL_C = tuple(val % 4 for val in range(16))

    tiles = s.tiles

    md = 0 # Manhattan Distance
    for i, val in enumerate(tiles):
        if val != 0: # Ignore the blank tile
            md += MD_TABLE[i][val]

    lc = 0 # Linear Conflicts (each conflict adds 2 to the base value)
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

    cc = 0 # Corner Conflicts
    # If a corner tile is in its final place but its adjacent tiles are not,
    # it creates a difficult-to-resolve block.
    # Top-right corner (tile 3 at index 3)
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        cc += 2
    # Bottom-left corner (tile 12 at index 12)
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        cc += 2
    # Bottom-right corner (tile 15 at index 15)
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        cc += 2

    # Base heuristic: Manhattan distance + Weighted Linear Conflicts + Corner Conflicts.
    # The LC weight is increased from 8 to 9, the next logical step in the evolution.
    base_h = md + lc * 9 + cc

    # The overall greedy multiplier is maintained at 3.6, which has proven effective.
    return int(base_h * 3.6)