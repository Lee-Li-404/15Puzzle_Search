from fifteen_state_class import State

def heuristic(s: State) -> int:
    """Calculates a heuristic for the 15-puzzle using Manhattan distance with a lookup table for goal positions.

    This heuristic estimates the minimum number of moves required to reach the goal state.
    It iterates through each tile, calculates its Manhattan distance to its goal position, and sums these distances.
    The blank tile (0) is ignored.
    """
    # Lookup table for goal positions (row, col) for each tile value.
    # Tile 0 is blank, goal position is (0, 0).
    # Tile 1 is at (0, 1), Tile 2 at (0, 2), ..., Tile 15 at (3, 3).
    GOAL_POS = [
        (0, 0), (0, 1), (0, 2), (0, 3),
        (1, 0), (1, 1), (1, 2), (1, 3),
        (2, 0), (2, 1), (2, 2), (2, 3),
        (3, 0), (3, 1), (3, 2), (3, 3)
    ]

    dist = 0
    for i, tile_value in enumerate(s.tiles):
        if tile_value == 0:
            continue  # Skip the blank tile

        # Get the current row and column of the tile.
        current_row, current_col = divmod(i, 4)

        # Get the goal row and column for this tile value.
        goal_row, goal_col = GOAL_POS[tile_value]

        # Calculate Manhattan distance for this tile.
        # Manhattan distance = |current_row - goal_row| + |current_col - goal_col|
        dist += abs(current_row - goal_row) + abs(current_col - goal_col)

    return dist
