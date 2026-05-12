from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic combines Manhattan distance with a highly weighted linear conflicts penalty.
    Linear conflicts occur when two tiles are in their correct row or column but are
    in the wrong order relative to each other. Resolving a conflict requires at least
    two extra moves.

    To make the heuristic even greedier and further reduce the number of generated nodes,
    this implementation uses an increased weight of 5 for each conflict (up from 4).
    This makes the heuristic strongly non-admissible, aiming for a better trade-off
    between search speed (fewer nodes) and solution optimality, while staying within
    the allowed 1.80 cost_ratio. The higher weight prioritizes pruning search space.
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
    for i, val in enumerate(tiles):
        if val == 0:  # Skip the blank tile.
            continue
        goal_r, goal_c = GOAL_POS[val]
        cur_r, cur_c = divmod(i, 4)
        manhattan_distance += abs(goal_r - cur_r) + abs(goal_c - cur_c)

    linear_conflicts = 0

    # Calculate row conflicts.
    for r in range(4):
        for c1 in range(4):
            val1 = tiles[r * 4 + c1]
            if val1 == 0 or GOAL_POS[val1][0] != r:
                continue

            for c2 in range(c1 + 1, 4):
                val2 = tiles[r * 4 + c2]
                if val2 != 0 and GOAL_POS[val2][0] == r and GOAL_POS[val1][1] > GOAL_POS[val2][1]:
                    linear_conflicts += 1

    # Calculate column conflicts.
    for c in range(4):
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            if val1 == 0 or GOAL_POS[val1][1] != c:
                continue

            for r2 in range(r1 + 1, 4):
                val2 = tiles[r2 * 4 + c]
                if val2 != 0 and GOAL_POS[val2][1] == c and GOAL_POS[val1][0] > GOAL_POS[val2][0]:
                    linear_conflicts += 1

    # The total heuristic is the Manhattan distance plus a heavily weighted penalty for linear conflicts.
    # A weight of 5 is used to further increase the heuristic's greediness, aiming to reduce
    # the number of generated nodes.
    return manhattan_distance + 5 * linear_conflicts