from fifteen_state_class import State

#  train nodes:  0.000435 | train worst cost:  1.448980 | test nodes:  0.000362 | test worst cost:  1.566038
#  set cost bound during training: 1.45  
def heuristic(s: State) -> int:
    """
    An aggressive, inadmissible heuristic designed to significantly reduce the number of generated nodes.
    It builds upon the successful strategy of the previous best heuristic by further:

    1. Increasing the overall WEIGHT: To be more greedy and explore promising paths first.
    2. Refining Linear Conflict penalties: Differentiating penalties for row and column conflicts,
       and introducing row-specific weights for LC, encouraging a top-down solving strategy.
    3. Enhancing Corner Conflict detection: Adding a more robust check for tiles trapped in corners.

    The heuristic combines Weighted Manhattan Distance, Row/Column Linear Conflicts, and Corner Conflicts.
    H = WEIGHT * (Weighted_MD + Row_LC + Col_LC + Corner_C)
    """

    # Constants for heuristic calculation
    # This weight is aggressively chosen to prune the search space significantly.
    # It's expected to be > 1 to achieve the generated_ratio goal.
    WEIGHT = 1.5  

    # Row-specific weights for Manhattan Distance, encouraging top-down solving.
    # Higher weights for earlier rows means mistakes in earlier rows are penalized more.
    ROW_MD_WEIGHT = (2.0, 1.8, 1.5, 1.2) 

    # Penalties for linear conflicts. Row conflicts are weighted slightly higher
    # to prioritize resolving conflicts in upper rows first.
    ROW_LC_PENALTY = 3.5
    COL_LC_PENALTY = 3.0

    # Penalty for tiles trapped in specific corner configurations.
    # These are hard-to-move tiles and deserve a higher penalty.
    CORNER_PENALTY = 5.0

    tiles = s.tiles
    h_value = 0.0

    # Data structures to help calculate linear conflicts efficiently.
    # `tiles_in_goal_row[r]` will store (value, current_col) for tiles that belong in row `r`.
    # `tiles_in_goal_col[c]` will store (value, current_row) for tiles that belong in column `c`.
    tiles_in_goal_row = [[] for _ in range(4)]
    tiles_in_goal_col = [[] for _ in range(4)]

    # --- Weighted Manhattan Distance and Linear Conflict Pre-computation ---
    for i, val in enumerate(tiles):
        if val == 0: # Skip the blank tile
            continue

        # Calculate current row and column from index i
        curr_r, curr_c = divmod(i, 4)
        # Calculate goal row and column from tile value
        goal_r, goal_c = divmod(val, 4)

        # Weighted Manhattan Distance calculation
        # Each tile's Manhattan distance is multiplied by a weight specific to its goal row.
        h_value += (abs(goal_r - curr_r) + abs(goal_c - curr_c)) * ROW_MD_WEIGHT[goal_r]

        # Store tile information for linear conflict calculations if it's in its goal row or column.
        # This avoids a second pass over the tiles later.
        if curr_r == goal_r:
            tiles_in_goal_row[curr_r].append((val, curr_c))
        if curr_c == goal_c:
            tiles_in_goal_col[curr_c].append((val, curr_r))

    # --- Row Linear Conflicts ---
    for r in range(4):
        row_tiles = tiles_in_goal_row[r]
        # A linear conflict can only occur if there are at least two tiles in the row.
        if len(row_tiles) > 1:
            # Sort tiles by their current column position to easily detect inversions.
            row_tiles.sort(key=lambda x: x[1])
            for i in range(len(row_tiles)):
                val_a, c_a = row_tiles[i]
                goal_ca = val_a % 4 # Goal column for tile_a
                for j in range(i + 1, len(row_tiles)):
                    val_b, c_b = row_tiles[j]
                    goal_cb = val_b % 4 # Goal column for tile_b
                    # If two tiles are in the same goal row, but their goal columns are out of order (i.e., val_a should come after val_b in goal), it's a linear conflict.
                    if goal_ca > goal_cb:
                        h_value += ROW_LC_PENALTY

    # --- Column Linear Conflicts ---
    for c in range(4):
        col_tiles = tiles_in_goal_col[c]
        # A linear conflict can only occur if there are at least two tiles in the column.
        if len(col_tiles) > 1:
            # Sort tiles by their current row position.
            col_tiles.sort(key=lambda x: x[1])
            for i in range(len(col_tiles)):
                val_a, r_a = col_tiles[i]
                goal_ra = val_a // 4 # Goal row for tile_a
                for j in range(i + 1, len(col_tiles)):
                    val_b, r_b = col_tiles[j]
                    goal_rb = val_b // 4 # Goal row for tile_b
                    # If two tiles are in the same goal column, but their goal rows are out of order, it's a linear conflict.
                    if goal_ra > goal_rb:
                        h_value += COL_LC_PENALTY

    # --- Enhanced Corner Conflicts ---
    # These are specific patterns where tiles in corner positions are blocked by tiles 
    # that are already in their correct goal positions. These are notoriously hard to resolve.

    # Top-Left corner (position 0): Goal value is 0 (blank)
    # If tile 0 is NOT the blank, AND tile 1 is in its goal position (pos 1), AND tile 4 is in its goal position (pos 4).
    if tiles[0] != 0 and tiles[1] == 1 and tiles[4] == 4:
        h_value += CORNER_PENALTY

    # Top-Right corner (position 3): Goal value is 3
    # If tile 3 is not 3 (its goal value) AND not blank, AND tile 2 is in its goal position (pos 2), AND tile 7 is in its goal position (pos 7).
    if tiles[3] != 3 and tiles[3] != 0 and tiles[2] == 2 and tiles[7] == 7:
        h_value += CORNER_PENALTY

    # Bottom-Left corner (position 12): Goal value is 12
    # If tile 12 is not 12 AND not blank, AND tile 8 is in its goal position (pos 8), AND tile 13 is in its goal position (pos 13).
    if tiles[12] != 12 and tiles[12] != 0 and tiles[8] == 8 and tiles[13] == 13:
        h_value += CORNER_PENALTY

    # Bottom-Right corner (position 15): Goal value is 15
    # If tile 15 is not 15 AND not blank, AND tile 11 is in its goal position (pos 11), AND tile 14 is in its goal position (pos 14).
    if tiles[15] != 15 and tiles[15] != 0 and tiles[11] == 11 and tiles[14] == 14:
        h_value += CORNER_PENALTY

    # Apply the overall aggressive weight and cast to integer.
    return int(h_value * WEIGHT)
