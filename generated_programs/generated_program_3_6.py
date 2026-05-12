from fifteen_state_class import State

def heuristic(s: State) -> int:
    GRID_SIZE = 4

    dist = 0

    # Manhattan distance for each tile
    for i, val in enumerate(s.tiles):
        if val == 0:
            continue
        cur_r, cur_c = divmod(i, GRID_SIZE)
        # For tile 'val', its goal position is index 'val'.
        # So, its goal row is val // GRID_SIZE and goal column is val % GRID_SIZE.
        goal_r, goal_c = divmod(val, GRID_SIZE)
        dist += abs(goal_r - cur_r) + abs(goal_c - cur_c)

    # Add penalty for linear conflicts.
    # A linear conflict occurs when two tiles are in the same row (or column)
    # and their goal positions are also in the same row (or column),
    # but they are in the wrong order relative to each other.

    # Check rows for linear conflicts
    for r in range(GRID_SIZE):
        # Collect tiles that belong in this row (goal_r == r)
        tiles_in_row_goal = []
        for c in range(GRID_SIZE):
            idx = r * GRID_SIZE + c
            tile_val = s.tiles[idx]
            if tile_val != 0:
                goal_r_for_tile = divmod(tile_val, GRID_SIZE)[0]
                if goal_r_for_tile == r:
                    tiles_in_row_goal.append((tile_val, c)) # Store (tile_value, current_column)

        # If there are fewer than 2 tiles in this row that belong here, no conflict possible.
        if len(tiles_in_row_goal) < 2: 
            continue

        # Sort these tiles by their current column index.
        # This ensures cur_c1 < cur_c2 when checking pairs (i, j).
        tiles_in_row_goal.sort(key=lambda x: x[1])

        # Check for inversions in their goal column positions.
        for i in range(len(tiles_in_row_goal)):
            for j in range(i + 1, len(tiles_in_row_goal)):
                val1, cur_c1 = tiles_in_row_goal[i]
                val2, cur_c2 = tiles_in_row_goal[j]
                goal_c1 = divmod(val1, GRID_SIZE)[1]
                goal_c2 = divmod(val2, GRID_SIZE)[1]

                # If tiles are in the same goal row and in correct order in current positions,
                # but their goal columns are inverted relative to each other.
                if goal_c1 > goal_c2:
                    dist += 2 # Penalty for linear conflict

    # Check columns for linear conflicts
    for c in range(GRID_SIZE):
        # Collect tiles that belong in this column (goal_c == c)
        tiles_in_col_goal = []
        for r in range(GRID_SIZE):
            idx = r * GRID_SIZE + c
            tile_val = s.tiles[idx]
            if tile_val != 0:
                goal_c_for_tile = divmod(tile_val, GRID_SIZE)[1]
                if goal_c_for_tile == c:
                    tiles_in_col_goal.append((tile_val, r)) # Store (tile_value, current_row)

        # If there are fewer than 2 tiles in this column that belong here, no conflict possible.
        if len(tiles_in_col_goal) < 2:
            continue

        # Sort these tiles by their current row index.
        # This ensures cur_r1 < cur_r2 when checking pairs (i, j).
        tiles_in_col_goal.sort(key=lambda x: x[1])

        # Check for inversions in their goal row positions.
        for i in range(len(tiles_in_col_goal)):
            for j in range(i + 1, len(tiles_in_col_goal)):
                val1, cur_r1 = tiles_in_col_goal[i]
                val2, cur_r2 = tiles_in_col_goal[j]
                goal_r1 = divmod(val1, GRID_SIZE)[0]
                goal_r2 = divmod(val2, GRID_SIZE)[0]

                # If tiles are in the same goal column and in correct order in current positions,
                # but their goal rows are inverted relative to each other.
                if goal_r1 > goal_r2:
                    dist += 2 # Penalty for linear conflict

    return dist