from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic combines Manhattan distance with a weighted linear conflicts penalty.
    Linear conflicts occur when two tiles are in their correct row or column but are
    in the wrong order relative to each other. Resolving a conflict requires at least
    two extra moves.

    To make the heuristic greedier and reduce the number of generated nodes, this
    implementation uses a weight of 4 for each conflict. This makes the heuristic
    non-admissible, aiming for a better trade-off between search speed and solution
    optimality, while staying within the allowed cost_ratio.
    The weight is chosen to be high to prioritize reducing generated nodes.
    """
    # Pre-computed goal positions for each tile value (0-15).
    # GOAL_POS[tile_value] = (goal_row, goal_col)
    GOAL_POS = (
        (0, 0), (0, 1), (0, 2), (0, 3),
        (1, 0), (1, 1), (1, 2), (1, 3),
        (2, 0), (2, 1), (2, 2), (2, 3),
        (3, 0), (3, 1), (3, 2), (3, 3)
    )

    manhattan_distance = 0
    tiles = s.tiles

    # Calculate the total Manhattan distance.
    # For each tile, sum the absolute differences in row and column between its current and goal positions.
    for i, val in enumerate(tiles):
        if val == 0:  # Skip the blank tile.
            continue
        goal_r, goal_c = GOAL_POS[val]
        cur_r, cur_c = divmod(i, 4)  # Current row and column derived from index.
        manhattan_distance += abs(goal_r - cur_r) + abs(goal_c - cur_c)

    linear_conflicts = 0

    # Calculate row conflicts.
    # Iterate through each row.
    for r in range(4):
        # For each row, compare pairs of tiles.
        for c1 in range(4):
            val1 = tiles[r * 4 + c1]
            # A tile can only be in a row conflict if it's in its correct goal row.
            if val1 == 0 or GOAL_POS[val1][0] != r:
                continue

            for c2 in range(c1 + 1, 4):
                val2 = tiles[r * 4 + c2]
                # If tile2 is also in its goal row and the pair (val1, val2) is in the wrong order
                # relative to their goal positions within this row, it's a conflict.
                # (i.e., val1 is to the left of val2, but its goal column is to the right of val2's goal column).
                if val2 != 0 and GOAL_POS[val2][0] == r and GOAL_POS[val1][1] > GOAL_POS[val2][1]:
                    linear_conflicts += 1

    # Calculate column conflicts.
    # Iterate through each column.
    for c in range(4):
        # For each column, compare pairs of tiles.
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            # A tile can only be in a column conflict if it's in its correct goal column.
            if val1 == 0 or GOAL_POS[val1][1] != c:
                continue

            for r2 in range(r1 + 1, 4):
                val2 = tiles[r2 * 4 + c]
                # If tile2 is also in its goal column and the pair (val1, val2) is in the wrong order
                # relative to their goal positions within this column, it's a conflict.
                # (i.e., val1 is above val2, but its goal row is below val2's goal row).
                if val2 != 0 and GOAL_POS[val2][1] == c and GOAL_POS[val1][0] > GOAL_POS[val2][0]:
                    linear_conflicts += 1

    # The total heuristic is the Manhattan distance plus a weighted penalty for linear conflicts.
    # A weight of 4 is used to increase the heuristic's greediness, aiming to reduce
    # the number of generated nodes while keeping the cost_ratio within bounds.
    return manhattan_distance + 4 * linear_conflicts
