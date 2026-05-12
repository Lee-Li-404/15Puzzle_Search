from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic evolves the best-performing previous versions by making the
    search even more aggressive to minimize the number of generated nodes.
    It leverages the observation that prior successful heuristics had a
    cost_ratio well below the 1.80 limit, indicating room for a greedier approach.

    The core of the heuristic remains the highly effective weighted combination of:
    1. Manhattan Distance (MD): The sum of distances for each tile from its goal position.
    2. Linear Conflicts (LC): A heavy penalty (multiplied by 6) for tiles that are
       in their correct row/column but are in the wrong order relative to each other.
    3. Corner Conflicts (CC): A small penalty for corner tiles (3, 12, 15) that are
       in place but block their neighbors, hindering the final solution steps.

    The key improvement is increasing the final overall weighting factor from 3.5
    to 3.6. This small but significant change inflates the heuristic value further,
    forcing the A* search to prune more branches and focus on the most promising paths.

    The formula is: `int((MD + LC * 6 + CC) * 3.6)`.
    """

    # Precompute lookup tables for efficiency.
    MD_TABLE = tuple(
        tuple(
            abs((i // 4) - (val // 4)) + abs((i % 4) - (val % 4))
            for val in range(16)
        )
        for i in range(16)
    )
    GOAL_R = tuple(val // 4 for val in range(16))
    GOAL_C = tuple(val % 4 for val in range(16))

    tiles = s.tiles

    # 1. Manhattan Distance
    md = 0
    for i, val in enumerate(tiles):
        if val != 0:
            md += MD_TABLE[i][val]

    # 2. Linear Conflicts
    lc = 0
    # Row conflicts
    for r in range(4):
        for c1 in range(4):
            val1 = tiles[r * 4 + c1]
            if val1 == 0 or GOAL_R[val1] != r:
                continue
            for c2 in range(c1 + 1, 4):
                val2 = tiles[r * 4 + c2]
                if val2 != 0 and GOAL_R[val2] == r and val1 > val2:
                    lc += 2
    # Column conflicts
    for c in range(4):
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            if val1 == 0 or GOAL_C[val1] != c:
                continue
            for r2 in range(r1 + 1, 4):
                val2 = tiles[r2 * 4 + c]
                if val2 != 0 and GOAL_C[val2] == c and GOAL_R[val1] > GOAL_R[val2]:
                    lc += 2

    # 3. Corner Conflicts
    cc = 0
    # Top-right corner (tile 3)
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        cc += 2
    # Bottom-left corner (tile 12)
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        cc += 2
    # Bottom-right corner (tile 15)
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        cc += 2
    
    # Combine components with proven weights
    base_h = md + lc * 6 + cc

    # Apply the increased overall greedy weighting factor
    return int(base_h * 3.6)