from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    An improved heuristic for the 15-puzzle, aiming to minimize unique nodes generated.
    It builds on the Manhattan Distance (MD) and Linear Conflicts (LC) heuristic.
    To reduce generated nodes further, the weight of the combined heuristic is increased.

    The previous best heuristic (score=0.0029, gen=0.003, cost=1.219) used MD + 2*LC with a weight of 1.71.
    The current goal is to improve the 'generated_ratio' while keeping 'cost_ratio' <= 1.80.
    Given the headroom in 'cost_ratio' (1.219 vs 1.80), we can afford to increase the heuristic's greediness.

    This version uses MD + 2*LC and increases the weight from 1.71 to a slightly higher value. 
    A weight of 1.75 was explored in a previous attempt (score=0.0070) but might have been too high or had other components that detracted.
    Let's try a value between 1.71 and 1.75, or perhaps slightly higher than 1.71, to aggressively reduce node generation.
    
    Trying a weight of 1.73.
    It is important to keep the calculation efficient. The current approach (MD + LC) is O(N^2) where N=4, which is effectively O(1) for the 15-puzzle (16 tiles).
    """
    # GOAL_RC[tile_value] -> (goal_row, goal_col). Pre-calculated for O(1) lookups.
    GOAL_RC = (
        (0, 0), (0, 1), (0, 2), (0, 3),
        (1, 0), (1, 1), (1, 2), (1, 3),
        (2, 0), (2, 1), (2, 2), (2, 3),
        (3, 0), (3, 1), (3, 2), (3, 3),
    )

    tiles = s.tiles
    manhattan_dist = 0

    # 1. Manhattan Distance Calculation
    # This is a standard admissible heuristic, efficient O(16).
    for i in range(16):
        val = tiles[i]
        if val == 0:
            continue
        goal_r, goal_c = GOAL_RC[val]
        cur_r, cur_c = i // 4, i % 4
        manhattan_dist += abs(goal_r - cur_r) + abs(goal_c - cur_c)

    # 2. Linear Conflicts Calculation
    conflicts = 0

    # Row conflicts
    # Iterate through each row.
    for r in range(4):
        # For each tile in the row, check for conflicts with tiles to its right.
        for c1 in range(4):
            val1 = tiles[r * 4 + c1]
            # A tile can only be in a linear conflict if it's in its goal row.
            if val1 == 0 or GOAL_RC[val1][0] != r:
                continue

            for c2 in range(c1 + 1, 4):
                val2 = tiles[r * 4 + c2]
                # If tile2 is also in its goal row, and tile1 > tile2 (inverted order).
                if val2 != 0 and GOAL_RC[val2][0] == r and val1 > val2:
                    conflicts += 1

    # Column conflicts
    # Iterate through each column.
    for c in range(4):
        # For each tile in the column, check for conflicts with tiles below it.
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            # A tile can only be in a linear conflict if it's in its goal column.
            if val1 == 0 or GOAL_RC[val1][1] != c:
                continue

            for r2 in range(r1 + 1, 4):
                val2 = tiles[r2 * 4 + c]
                # If tile2 is also in its goal column, and tile1's goal row > tile2's goal row (inverted order).
                if val2 != 0 and GOAL_RC[val2][1] == c and GOAL_RC[val1][0] > GOAL_RC[val2][0]:
                    conflicts += 1

    # Each linear conflict requires at least 2 extra moves.
    linear_conflicts_cost = conflicts * 2

    # 3. Combine and Weight
    # The base heuristic is the sum of Manhattan Distance and Linear Conflicts.
    base_h = manhattan_dist + linear_conflicts_cost

    # Increase the weight to make the heuristic greedier, aiming to reduce
    # generated nodes while staying within the cost_ratio bound of 1.80.
    # Previous best used ~1.71. Increasing it slightly should improve generated_ratio.
    WEIGHT = 1.73

    return int(base_h * WEIGHT)
