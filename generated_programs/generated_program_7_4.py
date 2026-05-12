from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic combines Manhattan distance with a weighted linear conflicts penalty.
    Linear conflicts occur when two tiles are in their correct row or column but are
    in the wrong order relative to each other. Resolving a conflict requires at least
    two extra moves. The standard admissible heuristic adds 2 * (number of conflicts)
    to the Manhattan distance.

    To make the heuristic greedier and reduce the number of generated nodes, this
    implementation uses a weight of 3 for each conflict. This makes the heuristic
    non-admissible, aiming for a better trade-off between search speed and solution
    optimality, while staying within the allowed cost_ratio.
    """
    GOAL_POS = (
        (0, 0), (0, 1), (0, 2), (0, 3),
        (1, 0), (1, 1), (1, 2), (1, 3),
        (2, 0), (2, 1), (2, 2), (2, 3),
        (3, 0), (3, 1), (3, 2), (3, 3)
    )

    manhattan_distance = 0
    for i, val in enumerate(s.tiles):
        if val == 0:
            continue
        goal_r, goal_c = GOAL_POS[val]
        cur_r, cur_c = divmod(i, 4)
        manhattan_distance += abs(goal_r - cur_r) + abs(goal_c - cur_c)

    linear_conflicts = 0
    tiles = s.tiles

    # Row conflicts: For each row, check for pairs of tiles that are in their
    # correct row but are in the wrong order.
    for r in range(4):
        for c1 in range(4):
            val1 = tiles[r * 4 + c1]
            if val1 == 0 or GOAL_POS[val1][0] != r:
                continue
            for c2 in range(c1 + 1, 4):
                val2 = tiles[r * 4 + c2]
                if val2 != 0 and GOAL_POS[val2][0] == r and GOAL_POS[val1][1] > GOAL_POS[val2][1]:
                    linear_conflicts += 1

    # Column conflicts: For each column, check for pairs of tiles that are in
    # their correct column but are in the wrong order.
    for c in range(4):
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            if val1 == 0 or GOAL_POS[val1][1] != c:
                continue
            for r2 in range(r1 + 1, 4):
                val2 = tiles[r2 * 4 + c]
                if val2 != 0 and GOAL_POS[val2][1] == c and GOAL_POS[val1][0] > GOAL_POS[val2][0]:
                    linear_conflicts += 1
    
    # The total heuristic is the Manhattan distance plus a weighted penalty for conflicts.
    # Using a weight of 3 makes it non-admissible but greedier.
    return manhattan_distance + 3 * linear_conflicts