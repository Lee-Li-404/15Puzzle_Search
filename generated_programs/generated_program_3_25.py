from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic aggressively prunes the search space for the 15 Puzzle by
    combining Manhattan Distance, Linear Conflicts, and Corner Conflicts, with
    significantly increased weighting factors. The goal is to minimize generated
    nodes while ensuring the cost ratio remains below 1.80.

    It builds upon previous successful versions by further inflating the heuristic
    values to be greedier, leveraging the headroom in the cost ratio bound.

    The components are:
    1. Manhattan Distance (MD): Sum of absolute row and column differences for each tile
       from its goal position. O(1) with precomputed lookup.
    2. Linear Conflicts (LC): Penalizes tiles in their correct row/column but in the wrong
       order. Standard penalty of 2 per conflict, multiplied by 5 (`lc * 5`).
    3. Corner Conflicts (CC): Penalizes specific corner tiles (3, 12, 15) if they are in
       place but block adjacent tiles. Standard penalty of 2 per conflict.
    4. Overall Greedy Weighting: An aggressive factor of 3.4 is applied to the sum of
       weighted components. This factor is chosen to maximize pruning while staying
       within the cost_ratio bound.

    The formula is: `int((MD + LC * 5 + CC) * 3.4)`
    """

    # Precompute Manhattan Distance lookup table for O(1) access.
    # MD_TABLE[i][val] stores Manhattan distance for tile 'val' if it were at index 'i'.
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

    # 1. Manhattan Distance Calculation
    md = 0
    for i, val in enumerate(tiles):
        if val != 0:  # Ignore the blank tile (0)
            md += MD_TABLE[i][val]

    # 2. Linear Conflicts Calculation
    lc = 0
    # Check for row conflicts
    for r in range(4):
        for c1 in range(4):
            idx1 = r * 4 + c1
            val1 = tiles[idx1]
            # Tile must be non-blank and belong to this row 'r' in the goal state
            if val1 == 0 or GOAL_R[val1] != r:
                continue
            for c2 in range(c1 + 1, 4):
                idx2 = r * 4 + c2
                val2 = tiles[idx2]
                # Check if val2 is non-blank, belongs to this row 'r', and is in conflict
                # (val1 left of val2, but val1's goal column > val2's goal column)
                if val2 != 0 and GOAL_R[val2] == r and val1 > val2:
                    lc += 2  # Add 2 for each linear conflict

    # Check for column conflicts
    for c in range(4):
        for r1 in range(4):
            idx1 = r1 * 4 + c
            val1 = tiles[idx1]
            # Tile must be non-blank and belong to this column 'c' in the goal state
            if val1 == 0 or GOAL_C[val1] != c:
                continue
            for r2 in range(r1 + 1, 4):
                idx2 = r2 * 4 + c
                val2 = tiles[idx2]
                # Check if val2 is non-blank, belongs to this column 'c', and is in conflict
                # (val1 above val2, but val1's goal row > val2's goal row)
                if val2 != 0 and GOAL_C[val2] == c and GOAL_R[val1] > GOAL_R[val2]:
                    lc += 2  # Add 2 for each linear conflict

    # 3. Corner Conflicts Calculation
    cc = 0
    # Corner 3 (top-right index 3): Tile 3 in goal position but blocks others
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        cc += 2
    # Corner 12 (bottom-left index 12): Tile 12 in goal position but blocks others
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        cc += 2
    # Corner 15 (bottom-right index 15): Tile 15 in goal position but blocks others
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        cc += 2

    # Combine components with increased weights for greediness.
    # Linear conflicts are weighted more heavily (lc * 5).
    base_h = md + lc * 5 + cc

    # Apply an overall greedy weighting factor to further inflate the heuristic.
    # Increased to 3.4 to maximize node reduction, estimated to be around cost_ratio=1.77.
    return int(base_h * 3.4)
