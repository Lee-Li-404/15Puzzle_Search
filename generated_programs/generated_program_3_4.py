from fifteen_state_class import State

def heuristic(s: State) -> int:
    GRID_SIZE = 4
    GOAL_POS = [
        0,  1,  2,  3,
        4,  5,  6,  7,
        8,  9, 10, 11,
        12, 13, 14, 15
    ]

    dist = 0

    # Manhattan distance calculation
    for i, val in enumerate(s.tiles):
        if val == 0:
            continue
        cur_r, cur_c = divmod(i, GRID_SIZE)
        goal_r, goal_c = divmod(GOAL_POS[val], GRID_SIZE)
        dist += abs(goal_r - cur_r) + abs(goal_c - cur_c)

    # Simplified linear conflict detection for rows
    for r in range(GRID_SIZE):
        row_tiles_in_goal_row = []
        for c in range(GRID_SIZE):
            idx = r * GRID_SIZE + c
            tile_val = s.tiles[idx]
            if tile_val != 0:
                goal_r_for_tile, _ = divmod(GOAL_POS[tile_val], GRID_SIZE)
                if goal_r_for_tile == r:
                    row_tiles_in_goal_row.append((tile_val, GOAL_POS[tile_val] % GRID_SIZE))
        
        # Sort tiles by their goal column position
        row_tiles_in_goal_row.sort(key=lambda x: x[1])
        
        # Check for inversions in current column positions relative to goal column order
        for i in range(len(row_tiles_in_goal_row)):
            for j in range(i + 1, len(row_tiles_in_goal_row)):
                goal_c1 = row_tiles_in_goal_row[i][1]
                goal_c2 = row_tiles_in_goal_row[j][1]
                
                # Find current columns of these tiles to check their relative order
                current_c1 = -1
                current_c2 = -1
                for k in range(GRID_SIZE * GRID_SIZE):
                    if s.tiles[k] == row_tiles_in_goal_row[i][0]:
                        current_c1 = k % GRID_SIZE
                    if s.tiles[k] == row_tiles_in_goal_row[j][0]:
                        current_c2 = k % GRID_SIZE
                
                if current_c1 > current_c2: # Inverted order in current position
                    dist += 2 # Penalty for linear conflict in row

    # Simplified linear conflict detection for columns
    for c in range(GRID_SIZE):
        col_tiles_in_goal_col = []
        for r in range(GRID_SIZE):
            idx = r * GRID_SIZE + c
            tile_val = s.tiles[idx]
            if tile_val != 0:
                _, goal_c_for_tile = divmod(GOAL_POS[tile_val], GRID_SIZE)
                if goal_c_for_tile == c:
                    col_tiles_in_goal_col.append((tile_val, GOAL_POS[tile_val] // GRID_SIZE))
        
        # Sort tiles by their goal row position
        col_tiles_in_goal_col.sort(key=lambda x: x[1])
        
        # Check for inversions in current row positions relative to goal row order
        for i in range(len(col_tiles_in_goal_col)):
            for j in range(i + 1, len(col_tiles_in_goal_col)):
                goal_r1 = col_tiles_in_goal_col[i][1]
                goal_r2 = col_tiles_in_goal_col[j][1]

                # Find current rows of these tiles to check their relative order
                current_r1 = -1
                current_r2 = -1
                for k in range(GRID_SIZE * GRID_SIZE):
                    if s.tiles[k] == col_tiles_in_goal_col[i][0]:
                        current_r1 = k // GRID_SIZE
                    if s.tiles[k] == col_tiles_in_goal_col[j][0]:
                        current_r2 = k // GRID_SIZE

                if current_r1 > current_r2: # Inverted order in current position
                    dist += 2 # Penalty for linear conflict in column

    return dist
