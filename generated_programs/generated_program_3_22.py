from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic further evolves previous successful versions, aiming to maximize
    the reduction in unique nodes generated during A* search by increasing the
    greediness, while ensuring the cost_ratio remains within the 1.80 bound.

    It builds upon the robust combination of:
    1. Manhattan Distance (MD): The sum of Manhattan distances for each tile.
    2. Linear Conflicts (LC): Penalties for tiles in their correct row/column but
       in incorrect relative order. This term is heavily weighted (multiplied by 6).
    3. Corner Conflicts (CC): Penalties for specific corner tiles (3, 12, 15) that
       are in their goal position but block adjacent tiles.

    The primary modification in this version is increasing the overall weighting factor
    from 3.6 (in previous high-scoring versions) to 3.7. This aggressive inflation of
    the heuristic value is designed to prune the search tree even more effectively,
    leveraging the available headroom in the cost_ratio.

    The formula used is: `int((MD + LC * 6 + CC) * 3.7)`.
    """

    # Precompute lookup tables for efficiency.
    # MD_TABLE[i][val] stores Manhattan distance for tile 'val' if it were at index 'i'.
    MD_TABLE = tuple(
        tuple(
            abs((i // 4) - (val // 4)) + abs((i % 4) - (val % 4))
            for val in range(16)
        )
        for i in range(16)
    )
    # GOAL_R[val] and GOAL_C[val] store the goal row and column for tile 'val'.
    GOAL_R = tuple(val // 4 for val in range(16))
    GOAL_C = tuple(val % 4 for val in range(16))

    tiles = s.tiles

    # 1. Manhattan Distance Calculation
    md = 0
    for i, val in enumerate(tiles):
        if val != 0:  # Ignore the blank tile (0)
            md += MD_TABLE[i][val]

    # 2. Linear Conflicts Calculation
    lc = 0
    # Check for row conflicts
    for r in range(4):
        for c1 in range(4):
            val1 = tiles[r * 4 + c1]
            # Tile must be non-blank and belong to this row 'r' in the goal state
            if val1 == 0 or GOAL_R[val1] != r:
                continue
            for c2 in range(c1 + 1, 4):
                val2 = tiles[r * 4 + c2]
                # Tile must be non-blank, belong to this row 'r', and be in conflict
                # Conflict: val1 is to the left of val2 (c1 < c2), but val1's goal column is to the right of val2's goal column.
                if val2 != 0 and GOAL_R[val2] == r and val1 > val2:
                    lc += 2  # Add 2 for each linear conflict

    # Check for column conflicts
    for c in range(4):
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            # Tile must be non-blank and belong to this column 'c' in the goal state
            if val1 == 0 or GOAL_C[val1] != c:
                continue
            for r2 in range(r1 + 1, 4):
                val2 = tiles[r2 * 4 + c]
                # Tile must be non-blank, belong to this column 'c', and be in conflict
                # Conflict: val1 is above val2 (r1 < r2), but val1's goal row is below val2's goal row.
                if val2 != 0 and GOAL_C[val2] == c and GOAL_R[val1] > GOAL_R[val2]:
                    lc += 2  # Add 2 for each linear conflict

    # 3. Corner Conflicts Calculation
    cc = 0
    # Check top-right corner (tile 3 at index 3)
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        cc += 2
    # Check bottom-left corner (tile 12 at index 12)
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        cc += 2
    # Check bottom-right corner (tile 15 at index 15)
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        cc += 2

    # Combine components: MD + (LC * 6) + CC
    base_h = md + lc * 6 + cc

    # Apply an increased overall greedy weighting factor to inflate the heuristic.
    # Increased to 3.7 to further reduce generated nodes, relying on cost_ratio headroom.
    return int(base_h * 3.7)