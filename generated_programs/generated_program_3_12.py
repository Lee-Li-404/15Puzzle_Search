from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic builds upon the previous best (score=0.0009, cost_ratio=1.612).
    It retains the effective combination of Manhattan Distance (MD), an aggressively
    weighted Linear Conflicts (LC), and Corner Conflicts (CC). The primary modification
    is to further increase the overall greedy weighting factor to reduce the number of
    unique nodes generated, while aiming to stay within the cost_ratio <= 1.80 bound.

    The strategy is as follows:
    1.  Manhattan Distance (MD): Standard calculation for tile displacement.
    2.  Linear Conflicts (LC): Penalizes tiles in their correct row/column but in wrong order.
        The penalty multiplier remains at 5 (`lc * 5`), as this has proven to be a highly
        effective component for pruning.
    3.  Corner Conflicts (CC): Penalizes specific corner tiles (3, 12, 15) if they are in
        their goal position but are 'blocking' adjacent tiles from reaching theirs.
        The penalty multiplier remains at 2 for each such conflict.
    4.  Overall Weighting Factor: Increased from 2.9 to 3.2. This makes the A* search
        more greedy, inflating the heuristic value more aggressively. Based on previous
        results (cost_ratio 1.612 with 2.9), a factor of 3.2 is estimated to bring the
        worst-case cost_ratio closer to the 1.80 limit (estimated around 1.77-1.78),
        thereby maximizing the reduction in generated nodes.

    The heuristic is calculated as: `int((MD + LC * 5 + CC) * 3.2)`.
    """

    # Precompute Manhattan Distance lookup table for O(1) access
    MD_TABLE = tuple(
        tuple(
            abs((i // 4) - (val // 4)) + abs((i % 4) - (val % 4))
            for val in range(16)
        )
        for i in range(16)
    )

    # Precompute goal row and column for O(1) access
    GOAL_R = tuple(val // 4 for val in range(16))
    GOAL_C = tuple(val % 4 for val in range(16))

    tiles = s.tiles

    md = 0
    for i, val in enumerate(tiles):
        if val != 0: # Ignore the blank tile for MD
            md += MD_TABLE[i][val]

    lc = 0
    # Row conflicts
    for r in range(4):
        for c1 in range(4):
            idx1 = r * 4 + c1
            val1 = tiles[idx1]
            # Check if val1 is a non-blank tile and belongs to this row 'r'
            if val1 == 0 or GOAL_R[val1] != r:
                continue
            for c2 in range(c1 + 1, 4):
                idx2 = r * 4 + c2
                val2 = tiles[idx2]
                # Check if val2 is a non-blank tile, belongs to this row 'r', and is in conflict with val1
                if val2 != 0 and GOAL_R[val2] == r and val1 > val2:
                    lc += 2 # Add 2 for each linear conflict

    # Column conflicts
    for c in range(4):
        for r1 in range(4):
            idx1 = r1 * 4 + c
            val1 = tiles[idx1]
            # Check if val1 is a non-blank tile and belongs to this column 'c'
            if val1 == 0 or GOAL_C[val1] != c:
                continue
            for r2 in range(r1 + 1, 4):
                idx2 = r2 * 4 + c
                val2 = tiles[idx2]
                # Check if val2 is a non-blank tile, belongs to this column 'c', and is in conflict with val1
                if val2 != 0 and GOAL_C[val2] == c and GOAL_R[val1] > GOAL_R[val2]:
                    lc += 2 # Add 2 for each linear conflict

    cc = 0
    # Corner Conflicts: Penalize tiles if they are in a corner but block other tiles.
    # Top-right corner (tile 3 at index 3)
    if tiles[3] == 3: # If tile 3 is in its goal position
        # And either tile 2 (left of 3) is not 2 OR tile 7 (below 3) is not 7
        if tiles[2] != 2 or tiles[7] != 7:
            cc += 2
    
    # Bottom-left corner (tile 12 at index 12)
    if tiles[12] == 12: # If tile 12 is in its goal position
        # And either tile 8 (above 12) is not 8 OR tile 13 (right of 12) is not 13
        if tiles[8] != 8 or tiles[13] != 13:
            cc += 2

    # Bottom-right corner (tile 15 at index 15)
    if tiles[15] == 15: # If tile 15 is in its goal position
        # And either tile 11 (above 15) is not 11 OR tile 14 (left of 15) is not 14
        if tiles[11] != 11 or tiles[14] != 14:
            cc += 2

    # Combine all components. Linear conflicts are weighted more heavily (lc * 5).
    base_h = md + lc * 5 + cc

    # Apply an overall greedy weighting factor to further inflate the heuristic.
    # Increased from 2.9 to 3.2 to maximize node reduction while staying within cost_ratio limits.
    return int(base_h * 3.2)