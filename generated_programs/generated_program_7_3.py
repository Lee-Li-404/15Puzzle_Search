from fifteen_state_class import State

def heuristic(s: State) -> int:
    """Combines Manhattan distance with a penalty for misplaced tiles.

    This heuristic aims to be greedier than pure Manhattan distance to reduce
    the number of unique nodes generated, while staying within the cost ratio bound.
    It calculates the sum of Manhattan distances for all tiles and adds a penalty
    for each tile that is not in its correct goal position.
    """
    # Pre-compute goal positions for faster lookup
    GOAL_POS = [
        (0, 0), (0, 1), (0, 2), (0, 3),
        (1, 0), (1, 1), (1, 2), (1, 3),
        (2, 0), (2, 1), (2, 2), (2, 3),
        (3, 0), (3, 1), (3, 2), (3, 3)
    ]

    manhattan_distance = 0
    misplaced_tiles = 0

    for i, val in enumerate(s.tiles):
        if val == 0:  # Skip the blank tile
            continue

        # Get current row and column
        cur_r, cur_c = divmod(i, 4)
        # Get goal row and column for the current tile value
        goal_r, goal_c = GOAL_POS[val]

        # Calculate Manhattan distance for this tile
        md = abs(goal_r - cur_r) + abs(goal_c - cur_c)
        manhattan_distance += md

        # If the tile is not in its goal position, increment misplaced count
        if md > 0:
            misplaced_tiles += 1

    # The heuristic value is the sum of Manhattan distances plus the count of misplaced tiles.
    # This makes the heuristic value higher for states with more tiles out of place,
    # potentially leading to more aggressive pruning.
    return manhattan_distance + misplaced_tiles
