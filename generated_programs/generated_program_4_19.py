from fifteen_state_class import State

def heuristic(s: State) -> int:
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

    lc = 0 # Linear Conflicts (each conflict adds 2)
    # Row conflicts
    for r in range(4):
        # Collect tiles in this row that belong to this row in the goal state
        row_tiles_in_goal_row = [] # Stores (tile_value, current_column)
        for c_idx in range(4):
            val = tiles[r * 4 + c_idx]
            if val != 0 and GOAL_R[val] == r: # Tile val belongs to this row 'r' in the goal state
                row_tiles_in_goal_row.append((val, c_idx))
        
        # Check for conflicts within this row
        # A conflict exists if two tiles are in their goal row but are reversed
        # in order relative to their goal columns. (val1 > val2 given c1 < c2)
        for i in range(len(row_tiles_in_goal_row)):
            for j in range(i + 1, len(row_tiles_in_goal_row)):
                val1, c1 = row_tiles_in_goal_row[i]
                val2, c2 = row_tiles_in_goal_row[j]
                # Since c1 < c2 is guaranteed by loop, conflict if val1's goal_col > val2's goal_col
                # which is equivalent to val1 > val2 for tiles in the same row.
                if val1 > val2:
                    lc += 2 # Add penalty for this linear conflict

    # Column conflicts
    for c in range(4):
        # Collect tiles in this column that belong to this column in the goal state
        col_tiles_in_goal_col = [] # Stores (tile_value, current_row)
        for r_idx in range(4):
            val = tiles[r_idx * 4 + c]
            if val != 0 and GOAL_C[val] == c: # Tile val belongs to this column 'c' in the goal state
                col_tiles_in_goal_col.append((val, r_idx))
        
        # Check for conflicts within this column
        # A conflict exists if two tiles are in their goal column but are reversed
        # in order relative to their goal rows. (GOAL_R[val1] > GOAL_R[val2] given r1 < r2)
        for i in range(len(col_tiles_in_goal_col)):
            for j in range(i + 1, len(col_tiles_in_goal_col)):
                val1, r1 = col_tiles_in_goal_col[i]
                val2, r2 = col_tiles_in_goal_col[j]
                # Since r1 < r2 is guaranteed by loop, conflict if val1's goal_row > val2's goal_row
                if GOAL_R[val1] > GOAL_R[val2]:
                    lc += 2 # Add penalty for this linear conflict

    cc = 0 # Corner Conflicts
    # Top-right corner (tile 3 at index 3)
    # If tile 3 is in place, but 2 or 7 are not, it's a blocking configuration.
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        cc += 2
    # Bottom-left corner (tile 12 at index 12)
    # If tile 12 is in place, but 8 or 13 are not.
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        cc += 2
    # Bottom-right corner (tile 15 at index 15)
    # If tile 15 is in place, but 11 or 14 are not.
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        cc += 2

    # Base heuristic: Manhattan distance + Linear Conflicts * multiplier + Corner Conflicts
    # Increasing the linear conflict penalty from 7 to 8. This makes the heuristic 
    # more aggressive towards configurations that are known to be difficult to resolve,
    # aiming to further reduce the 'generated_ratio'.
    base_h = md + lc * 8 + cc

    # The overall greedy multiplier is maintained at 3.6, which has consistently 
    # provided a good balance between search pruning and solution quality. 
    # The increased LC penalty provides the desired extra greediness.
    return int(base_h * 3.6)