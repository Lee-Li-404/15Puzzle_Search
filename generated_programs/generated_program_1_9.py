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

    # Row conflicts: For tiles in their correct goal row, count pairs
    # that are in the wrong order relative to each other.
    for r in range(BOARD_SIZE):
        goal_cols = []
        for c in range(BOARD_SIZE):
            tile_value = s.tiles[r * BOARD_SIZE + c]
            if tile_value != 0 and GOAL_POS[tile_value][0] == r:
                goal_cols.append(GOAL_POS[tile_value][1])
        
        n = len(goal_cols)
        for i in range(n):
            for j in range(i + 1, n):
                if goal_cols[i] > goal_cols[j]:
                    linear_conflicts += 1

    # Column conflicts: For tiles in their correct goal column, count pairs
    # that are in the wrong order relative to each other.
    for c in range(BOARD_SIZE):
        goal_rows = []
        for r in range(BOARD_SIZE):
            tile_value = s.tiles[r * BOARD_SIZE + c]
            if tile_value != 0 and GOAL_POS[tile_value][1] == c:
                goal_rows.append(GOAL_POS[tile_value][0])

        n = len(goal_rows)
        for i in range(n):
            for j in range(i + 1, n):
                if goal_rows[i] > goal_rows[j]:
                    linear_conflicts += 1

    # The base heuristic combines Manhattan distance with the linear conflicts.
    # Each conflict requires at least two extra moves to resolve.
    base_heuristic_value = total_dist + (2 * linear_conflicts)

    # Apply an aggressive weight to make the heuristic greedy, aiming to minimize
    # the number of generated nodes. The previous best cost_ratio of 1.490 was well
    # below the 1.80 limit, so we can increase the weight significantly.
    WEIGHT = 2.8
    final_heuristic_value = round(WEIGHT * base_heuristic_value)

    return max(0, final_heuristic_value)