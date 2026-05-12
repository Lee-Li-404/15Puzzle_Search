from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic aims to minimize the number of generated nodes by increasing the
    greedy nature of the A* search, while staying within the cost_ratio <= 1.80 bound.

    It builds upon the effective combination of Manhattan Distance (MD), Linear Conflicts (LC),
    and Corner Conflicts (CC) from previous versions.

    Key modifications for this iteration:
    1. Increased Linear Conflict Weight: The penalty for linear conflicts is set to `lc * 7`.
       This aggressive weighting prioritizes resolving these difficult patterns.
    2. Increased Overall Weighting Factor: The final multiplier is set to `3.5`. This makes
       the heuristic more greedy, aiming to prune more search branches. This is a slight
       increase from 3.4, leveraging any remaining headroom in the cost_ratio bound.

    The heuristic is calculated as: `int((MD + LC * 7 + CC) * 3.5)`.
    """

    # Precompute Manhattan Distance lookup table for O(1) access.
    # MD_TABLE[i][val] gives the Manhattan distance for tile 'val' at index 'i'.
    MD_TABLE = (
        (0, 1, 2, 3, 1, 2, 3, 4, 2, 3, 4, 5, 3, 4, 5, 6),
        (1, 0, 1, 2, 2, 1, 2, 3, 3, 2, 3, 4, 4, 3, 4, 5),
        (2, 1, 0, 1, 3, 2, 1, 2, 4, 3, 2, 3, 5, 4, 3, 4),
        (3, 2, 1, 0, 4, 3, 2, 1, 5, 4, 3, 2, 6, 5, 4, 3),
        (1, 2, 3, 4, 0, 1, 2, 3, 1, 2, 3, 4, 2, 3, 4, 5),
        (2, 1, 2, 3, 1, 0, 1, 2, 2, 1, 2, 3, 3, 2, 3, 4),
        (3, 2, 1, 2, 2, 1, 0, 1, 3, 2, 1, 2, 4, 3, 2, 3),
        (4, 3, 2, 1, 3, 2, 1, 0, 4, 3, 2, 1, 5, 4, 3, 2),
        (2, 3, 4, 5, 1, 2, 3, 4, 0, 1, 2, 3, 1, 2, 3, 4),
        (3, 2, 3, 4, 2, 1, 2, 3, 1, 0, 1, 2, 2, 1, 2, 3),
        (4, 3, 2, 3, 3, 2, 1, 2, 2, 1, 0, 1, 3, 2, 1, 2),
        (5, 4, 3, 2, 4, 3, 2, 1, 3, 2, 1, 0, 4, 3, 2, 1),
        (3, 4, 5, 6, 2, 3, 4, 5, 1, 2, 3, 4, 0, 1, 2, 3),
        (4, 3, 4, 5, 3, 2, 3, 4, 2, 1, 2, 3, 1, 0, 1, 2),
        (5, 4, 3, 4, 4, 3, 2, 3, 3, 2, 1, 2, 2, 1, 0, 1),
        (6, 5, 4, 3, 5, 4, 3, 2, 4, 3, 2, 1, 3, 2, 1, 0)
    )

    # Precompute goal row and column for O(1) access.
    GOAL_R = (0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3)
    GOAL_C = (0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3)

    tiles = s.tiles

    md = 0
    for i, val in enumerate(tiles):
        if val != 0:  # Ignore the blank tile for MD
            md += MD_TABLE[i][val]

    lc = 0
    # Calculate Row Conflicts:
    # For each row, check pairs of tiles that belong to this row in the goal state.
    # If they are in the wrong column order relative to each other, add 2 to LC.
    for r in range(4):
        for c1 in range(4):
            idx1 = r * 4 + c1
            val1 = tiles[idx1]
            if val1 == 0 or GOAL_R[val1] != r:
                continue
            for c2 in range(c1 + 1, 4):
                idx2 = r * 4 + c2
                val2 = tiles[idx2]
                if val2 != 0 and GOAL_R[val2] == r and val1 > val2:
                    lc += 2

    # Calculate Column Conflicts:
    # For each column, check pairs of tiles that belong to this column in the goal state.
    # If they are in the wrong row order relative to each other, add 2 to LC.
    for c in range(4):
        for r1 in range(4):
            idx1 = r1 * 4 + c
            val1 = tiles[idx1]
            if val1 == 0 or GOAL_C[val1] != c:
                continue
            for r2 in range(r1 + 1, 4):
                idx2 = r2 * 4 + c
                val2 = tiles[idx2]
                if val2 != 0 and GOAL_C[val2] == c and GOAL_R[val1] > GOAL_R[val2]:
                    lc += 2

    cc = 0
    # Corner Conflicts: Penalize specific corner tiles if they are in their goal position
    # but are blocking adjacent tiles from reaching theirs.
    # Top-right corner (tile 3 at index 3)
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        cc += 2
    # Bottom-left corner (tile 12 at index 12)
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        cc += 2
    # Bottom-right corner (tile 15 at index 15)
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        cc += 2

    # Combine all components. Linear conflicts are weighted heavily (lc * 7).
    base_h = md + lc * 7 + cc

    # Apply an overall greedy weighting factor to further inflate the heuristic.
    # Increased from 3.4 to 3.5 to maximize node reduction.
    return int(base_h * 3.5)
