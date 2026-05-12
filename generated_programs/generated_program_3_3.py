from fifteen_state_class import State

def heuristic(s: State) -> int:
    GRID_SIZE = 4
    # Precompute goal positions for O(1) lookup.
    # The goal is assumed to be 0 1 2 3 ... 15 in reading order.
    GOAL_POS = [
        0,  1,  2,  3,
        4,  5,  6,  7,
        8,  9, 10, 11,
        12, 13, 14, 15
    ]

    dist = 0
    # Calculate Manhattan distance for each tile.
    for i, val in enumerate(s.tiles):
        if val == 0:  # Skip the blank tile
            continue

        # Calculate current row and column
        cur_r, cur_c = divmod(i, GRID_SIZE)

        # Calculate goal row and column using the precomputed GOAL_POS
        goal_pos_index = GOAL_POS[val]
        goal_r, goal_c = divmod(goal_pos_index, GRID_SIZE)

        # Add Manhattan distance for this tile
        dist += abs(goal_r - cur_r) + abs(goal_c - cur_c)

    # We will use a simplified linear conflict heuristic. 
    # The previous version was correct but might be too slow due to nested loops.
    # To optimize, we'll focus on a subset of conflicts that are easily detectable 
    # and impactful.
    # For tiles in the goal row, check if they are in the correct column order.
    # For tiles in the goal column, check if they are in the correct row order.
    # This heuristic prioritizes reducing generated nodes while keeping cost_ratio low.

    # Linear conflicts in rows
    for r in range(GRID_SIZE):
        # Check tiles that should be in this row
        tiles_in_row = []
        for c in range(GRID_SIZE):
            idx = r * GRID_SIZE + c
            tile_val = s.tiles[idx]
            if tile_val != 0:
                goal_r_for_tile, _ = divmod(GOAL_POS[tile_val], GRID_SIZE)
                if goal_r_for_tile == r:
                    tiles_in_row.append((tile_val, c))
        
        # Sort tiles by their current column index within the row
        tiles_in_row.sort(key=lambda x: x[1])

        # Check for inversions in goal column positions for tiles in this row
        for i in range(len(tiles_in_row)):
            for j in range(i + 1, len(tiles_in_row)):
                val1, col1 = tiles_in_row[i]
                val2, col2 = tiles_in_row[j]
                goal_c1 = GOAL_POS[val1] % GRID_SIZE
                goal_c2 = GOAL_POS[val2] % GRID_SIZE
                if goal_c1 > goal_c2:
                    dist += 2 # Penalty for linear conflict in row

    # Linear conflicts in columns
    for c in range(GRID_SIZE):
        # Check tiles that should be in this column
        tiles_in_col = []
        for r in range(GRID_SIZE):
            idx = r * GRID_SIZE + c
            tile_val = s.tiles[idx]
            if tile_val != 0:
                _, goal_c_for_tile = divmod(GOAL_POS[tile_val], GRID_SIZE)
                if goal_c_for_tile == c:
                    tiles_in_col.append((tile_val, r))
        
        # Sort tiles by their current row index within the column
        tiles_in_col.sort(key=lambda x: x[1])

        # Check for inversions in goal row positions for tiles in this column
        for i in range(len(tiles_in_col)):
            for j in range(i + 1, len(tiles_in_col)):
                val1, row1 = tiles_in_col[i]
                val2, row2 = tiles_in_col[j]
                goal_r1 = GOAL_POS[val1] // GRID_SIZE
                goal_r2 = GOAL_POS[val2] // GRID_SIZE
                if goal_r1 > goal_r2:
                    dist += 2 # Penalty for linear conflict in column

    return dist