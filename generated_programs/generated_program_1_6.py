from fifteen_state_class import State

def heuristic(s: State) -> int:
    BOARD_SIZE = 4
    # Pre-calculated goal positions (row, col) for each tile value.
    GOAL_POS = [
        (0, 0), (0, 1), (0, 2), (0, 3),
        (1, 0), (1, 1), (1, 2), (1, 3),
        (2, 0), (2, 1), (2, 2), (2, 3),
        (3, 0), (3, 1), (3, 2), (3, 3)
    ]

    total_dist = 0

    # Calculate Manhattan distance for all non-blank tiles.
    for i, tile_value in enumerate(s.tiles):
        if tile_value == 0:
            continue
        current_row, current_col = divmod(i, BOARD_SIZE)
        goal_row, goal_col = GOAL_POS[tile_value]
        total_dist += abs(current_row - goal_row) + abs(current_col - goal_col)

    # Calculate Linear Conflicts.
    linear_conflicts = 0

    # Check rows for conflicts.
    for r in range(BOARD_SIZE):
        in_row_tiles = []
        for c in range(BOARD_SIZE):
            tile_value = s.tiles[r * BOARD_SIZE + c]
            if tile_value != 0 and GOAL_POS[tile_value][0] == r:
                in_row_tiles.append((c, GOAL_POS[tile_value][1]))
        
        n = len(in_row_tiles)
        for i in range(n):
            for j in range(i + 1, n):
                if in_row_tiles[i][0] < in_row_tiles[j][0] and in_row_tiles[i][1] > in_row_tiles[j][1]:
                    linear_conflicts += 1

    # Check columns for conflicts.
    for c in range(BOARD_SIZE):
        in_col_tiles = []
        for r in range(BOARD_SIZE):
            tile_value = s.tiles[r * BOARD_SIZE + c]
            if tile_value != 0 and GOAL_POS[tile_value][1] == c:
                in_col_tiles.append((r, GOAL_POS[tile_value][0]))

        n = len(in_col_tiles)
        for i in range(n):
            for j in range(i + 1, n):
                if in_col_tiles[i][0] < in_col_tiles[j][0] and in_col_tiles[i][1] > in_col_tiles[j][1]:
                    linear_conflicts += 1

    # The base heuristic is Manhattan distance + 2 * linear conflicts.
    base_heuristic_value = total_dist + (2 * linear_conflicts)

    # Apply an aggressive weight to be greedy and reduce generated nodes.
    # Previous results show that a high weight is effective and the cost_ratio
    # stays well within the 1.80 bound. We push this even further to minimize
    # the search space explored, accepting a higher solution cost.
    WEIGHT = 2.3
    
    final_heuristic_value = round(WEIGHT * base_heuristic_value)
    
    return max(0, final_heuristic_value)