from fifteen_state_class import State

def heuristic(s: State) -> int:
    MANHATTAN_DISTANCE = 0
    LINEAR_CONFLICTS = 0
    # Experimentally found that a WEIGHT around 3.0-3.2 seems to perform well for reducing generated nodes
    # while keeping cost_ratio within acceptable bounds. Let's try 3.2.
    WEIGHT = 3.2

    # Precompute goal positions: tile `val` goes to (row, col) = (val // 4, val % 4)
    goal_positions = (
        (0, 0), (0, 1), (0, 2), (0, 3),
        (1, 0), (1, 1), (1, 2), (1, 3),
        (2, 0), (2, 1), (2, 2), (2, 3),
        (3, 0), (3, 1), (3, 2), (3, 3)
    )

    # Precompute current positions for O(1) lookup: current_positions[val] = (current_row, current_col)
    current_positions = [None] * 16
    for i, val in enumerate(s.tiles):
        current_positions[val] = (i // 4, i % 4)

    # Calculate Manhattan Distance
    for val in range(1, 16): # Skip the blank tile (0)
        cur_r, cur_c = current_positions[val]
        goal_r, goal_c = goal_positions[val]
        MANHATTAN_DISTANCE += abs(goal_r - cur_r) + abs(goal_c - cur_c)

    # Calculate Linear Conflicts
    # A linear conflict occurs when two tiles are in the same row/column,
    # they both belong in that row/column (goal position), but they are in reverse order.
    # Each such conflict adds 2 to the heuristic.

    # Row conflicts
    for r in range(4):
        row_tiles_in_place = []
        for c_idx in range(4):
            val = s.tiles[r * 4 + c_idx]
            if val != 0 and goal_positions[val][0] == r: # Check if tile belongs in this row
                row_tiles_in_place.append((val, c_idx, goal_positions[val][1]))

        n_row_tiles = len(row_tiles_in_place)
        for i in range(n_row_tiles):
            val_a, cur_c_a, goal_c_a = row_tiles_in_place[i]
            for j in range(i + 1, n_row_tiles):
                val_b, cur_c_b, goal_c_b = row_tiles_in_place[j]

                # Conflict condition: A is to the right of B, but goal A is to the left of goal B
                if (cur_c_a > cur_c_b and goal_c_a < goal_c_b) or 
                   (cur_c_b > cur_c_a and goal_c_b < goal_c_a):
                    LINEAR_CONFLICTS += 1

    # Column conflicts
    for c in range(4):
        col_tiles_in_place = []
        for r_idx in range(4):
            val = s.tiles[r_idx * 4 + c]
            if val != 0 and goal_positions[val][1] == c: # Check if tile belongs in this column
                col_tiles_in_place.append((val, r_idx, goal_positions[val][0]))

        n_col_tiles = len(col_tiles_in_place)
        for i in range(n_col_tiles):
            val_a, cur_r_a, goal_r_a = col_tiles_in_place[i]
            for j in range(i + 1, n_col_tiles):
                val_b, cur_r_b, goal_r_b = col_tiles_in_place[j]

                # Conflict condition
                if (cur_r_a > cur_r_b and goal_r_a < goal_r_b) or 
                   (cur_r_b > cur_r_a and goal_r_b < goal_r_a):
                    LINEAR_CONFLICTS += 1

    # Apply weight to the combined Manhattan Distance and Linear Conflicts estimate
    return int((MANHATTAN_DISTANCE + (LINEAR_CONFLICTS * 2)) * WEIGHT)
