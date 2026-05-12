from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic function is designed for the 15 Puzzle, aiming to minimize the
    total number of unique nodes generated during A* search while keeping the
    cost_ratio (solution_length / optimal_solution_length) within 1.80.

    It combines three well-known heuristic components:
    1.  Manhattan Distance (MD): The sum of Manhattan distances for each tile
        from its goal position.
    2.  Linear Conflicts (LC): A heavy penalty (multiplied by 6) for tiles that are
        in their correct row or column but are in the wrong order relative to each other.
    3.  Corner Conflicts (CC): A small penalty for specific corner tiles (3, 12, 15)
        that are in their goal position but block adjacent tiles, making them harder to move.

    The heuristic applies an overall greedy weighting factor of 3.6 to the sum of
    these components. This factor has been optimized to aggressively prune the search
    space and reduce generated nodes, based on empirical performance in previous rounds.

    The formula used is: `int((MD + LC * 6 + CC) * 3.6)`.
    """

    # Precompute lookup tables for efficiency. These are constant for a 4x4 grid.
    # MD_TABLE[i][val] stores Manhattan distance for tile 'val' if it were at index 'i'.
    MD_TABLE = tuple(
        tuple(
            abs((i // 4) - (val // 4)) + abs((i % 4) - (val % 4))
            for val in range(16)
        )
        for i in range(16)
    )
    # GOAL_R[val] and GOAL_C[val] store the goal row and column for tile 'val'.
    GOAL_R = tuple(val // 4 for val in range(16))
    GOAL_C = tuple(val % 4 for val in range(16))

    tiles = s.tiles

    # 1. Manhattan Distance Calculation
    md = 0
    for i, val in enumerate(tiles):
        if val != 0:  # Ignore the blank tile (0) as it has no fixed goal position
            md += MD_TABLE[i][val]

    # 2. Linear Conflicts Calculation
    lc = 0
    # Check for row conflicts
    for r in range(4):
        for c1 in range(4):
            val1 = tiles[r * 4 + c1]
            # Tile must be non-blank and belong to this row 'r' in the goal state
            if val1 == 0 or GOAL_R[val1] != r:
                continue
            for c2 in range(c1 + 1, 4):
                val2 = tiles[r * 4 + c2]
                # Tile must be non-blank, belong to this row 'r', and be in conflict:
                # val1 is to the left of val2 (c1 < c2), but val1's goal column is to the right of val2's goal column.
                # For standard goal configuration, val1 > val2 implies GOAL_C[val1] > GOAL_C[val2]
                if val2 != 0 and GOAL_R[val2] == r and val1 > val2:
                    lc += 2  # Add 2 for each linear conflict (standard admissible penalty)

    # Check for column conflicts
    for c in range(4):
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            # Tile must be non-blank and belong to this column 'c' in the goal state
            if val1 == 0 or GOAL_C[val1] != c:
                continue
            for r2 in range(r1 + 1, 4):
                val2 = tiles[r2 * 4 + c]
                # Tile must be non-blank, belong to this column 'c', and be in conflict:
                # val1 is above val2 (r1 < r2), but val1's goal row is below val2's goal row.
                if val2 != 0 and GOAL_C[val2] == c and GOAL_R[val1] > GOAL_R[val2]:
                    lc += 2  # Add 2 for each linear conflict

    # 3. Corner Conflicts Calculation
    cc = 0
    # Corner 3 (top-right): Tile 3 is in its goal position but adjacent tiles are not
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        cc += 2
    # Corner 12 (bottom-left): Tile 12 is in its goal position but adjacent tiles are not
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        cc += 2
    # Corner 15 (bottom-right): Tile 15 is in its goal position but adjacent tiles are not
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        cc += 2

    # Combine components: MD + (LC * 6) + CC
    # Linear conflicts are weighted more heavily (x6) for greediness.
    base_h = md + lc * 6 + cc

    # Apply an overall greedy weighting factor to further inflate the heuristic.
    # This factor (3.6) is chosen to aggressively prune search nodes while maintaining
    # the cost_ratio constraint.
    return int(base_h * 3.6)