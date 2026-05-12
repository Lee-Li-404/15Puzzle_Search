from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic is an evolution of the linear conflicts heuristic. It combines
    Manhattan distance with a more aggressive weighted penalty for linear conflicts.
    A linear conflict occurs when two tiles are in their correct row or column but
    are in the wrong order, requiring at least two extra moves to resolve.

    The standard admissible version adds 2 * (number of conflicts). Previous
    versions used a weight of 3. To further reduce the number of generated nodes,
    this implementation uses an even larger weight of 4. This increases the
    heuristic's greediness, aiming to prune more of the search space at the risk
    of finding slightly more suboptimal paths, while staying within the 1.80
    cost_ratio constraint.
    """
    # Pre-computed goal positions for each tile value. Using a tuple for immutability.
    GOAL_POS = tuple((v // 4, v % 4) for v in range(16))

    manhattan_distance = 0
    tiles = s.tiles

    # Calculate the total Manhattan distance for all tiles.
    for i, val in enumerate(tiles):
        if val == 0:
            continue
        goal_r, goal_c = GOAL_POS[val]
        cur_r, cur_c = divmod(i, 4)
        manhattan_distance += abs(goal_r - cur_r) + abs(goal_c - cur_c)

    linear_conflicts = 0

    # Calculate row conflicts.
    for r in range(4):
        for c1 in range(4):
            val1 = tiles[r * 4 + c1]
            # A tile can only be in a conflict if it's in its goal row.
            if val1 == 0 or GOAL_POS[val1][0] != r:
                continue
            
            for c2 in range(c1 + 1, 4):
                val2 = tiles[r * 4 + c2]
                # If tile2 is also in its goal row and the pair is inverted,
                # it's a conflict. (val1 is to the left of val2, but its goal column is to the right of val2's goal column).
                if val2 != 0 and GOAL_POS[val2][0] == r and GOAL_POS[val1][1] > GOAL_POS[val2][1]:
                    linear_conflicts += 1

    # Calculate column conflicts.
    for c in range(4):
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            # A tile can only be in a conflict if it's in its goal column.
            if val1 == 0 or GOAL_POS[val1][1] != c:
                continue

            for r2 in range(r1 + 1, 4):
                val2 = tiles[r2 * 4 + c]
                # If tile2 is also in its goal column and the pair is inverted,
                # it's a conflict. (val1 is above val2, but its goal row is below val2's goal row).
                if val2 != 0 and GOAL_POS[val2][1] == c and GOAL_POS[val1][0] > GOAL_POS[val2][0]:
                    linear_conflicts += 1
    
    # The heuristic is Manhattan distance plus a heavily weighted linear conflict penalty.
    # The weight of 4 is chosen to make the heuristic very greedy.
    return manhattan_distance + 4 * linear_conflicts