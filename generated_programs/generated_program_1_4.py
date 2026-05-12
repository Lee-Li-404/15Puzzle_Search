from fifteen_state_class import State

def heuristic(s: State) -> int:
    BOARD_SIZE = 4
    # Lookup table for goal positions (row, col) for each tile value.
    # Tile 0 (blank) is at (0, 0), Tile 1 at (0, 1), etc.
    GOAL_POS = [
        (0, 0), (0, 1), (0, 2), (0, 3),
        (1, 0), (1, 1), (1, 2), (1, 3),
        (2, 0), (2, 1), (2, 2), (2, 3),
        (3, 0), (3, 1), (3, 2), (3, 3)
    ]

    total_dist = 0

    # Calculate Manhattan distance
    for i, tile_value in enumerate(s.tiles):
        if tile_value == 0:
            continue # Skip the blank tile
        current_row, current_col = divmod(i, BOARD_SIZE)
        goal_row, goal_col = GOAL_POS[tile_value]
        total_dist += abs(current_row - goal_row) + abs(current_col - goal_col)

    # Calculate Linear Conflicts
    linear_conflicts = 0

    # Check rows for linear conflicts
    for r in range(BOARD_SIZE):
        # Collect tiles that belong in this row and are currently in this row.
        # Stores (current_column, goal_column) for such tiles.
        in_row_tiles = []
        for c in range(BOARD_SIZE):
            tile_value = s.tiles[r * BOARD_SIZE + c]
            if tile_value == 0:
                continue
            goal_row, goal_col = GOAL_POS[tile_value]
            if goal_row == r: # Tile's goal row is the current row 'r'
                in_row_tiles.append((c, goal_col))

        # Check for conflicts within this specific row's relevant tiles.
        n_tiles_in_row = len(in_row_tiles)
        for i in range(n_tiles_in_row):
            for j in range(i + 1, n_tiles_in_row):
                cur_c1, goal_c1 = in_row_tiles[i]
                cur_c2, goal_c2 = in_row_tiles[j]

                # A linear conflict occurs if tile1 is to the left of tile2,
                # but tile1's goal position is to the right of tile2's goal position.
                if cur_c1 < cur_c2 and goal_c1 > goal_c2:
                    linear_conflicts += 1

    # Check columns for linear conflicts
    for c in range(BOARD_SIZE):
        # Collect tiles that belong in this column and are currently in this column.
        # Stores (current_row, goal_row) for such tiles.
        in_col_tiles = []
        for r in range(BOARD_SIZE):
            tile_value = s.tiles[r * BOARD_SIZE + c]
            if tile_value == 0:
                continue
            goal_row, goal_col = GOAL_POS[tile_value]
            if goal_col == c: # Tile's goal column is the current column 'c'
                in_col_tiles.append((r, goal_row))

        # Check for conflicts within this specific column's relevant tiles.
        n_tiles_in_col = len(in_col_tiles)
        for i in range(n_tiles_in_col):
            for j in range(i + 1, n_tiles_in_col):
                cur_r1, goal_r1 = in_col_tiles[i]
                cur_r2, goal_r2 = in_col_tiles[j]

                # A linear conflict occurs if tile1 is above tile2,
                # but tile1's goal position is below tile2's goal position.
                if cur_r1 < cur_r2 and goal_r1 > goal_r2:
                    linear_conflicts += 1

    # Each linear conflict requires at least 2 extra moves.
    # The base heuristic is Manhattan distance plus 2 * linear conflicts.
    base_heuristic_value = total_dist + (2 * linear_conflicts)

    # Apply a weight to make the heuristic greedier and further reduce generated nodes.
    # The previous best heuristic used WEIGHT = 1.5, which resulted in a cost_ratio of 1.143.
    # Since 1.143 is well below the 1.80 bound, we can safely increase the weight to make it greedier.
    # A weight of 1.75 is chosen to push for more node reduction while aiming to stay within the 1.80 cost_ratio bound.
    WEIGHT = 1.75
    final_heuristic_value = round(WEIGHT * base_heuristic_value)

    # Ensure the heuristic returns a non-negative integer.
    return max(0, final_heuristic_value)