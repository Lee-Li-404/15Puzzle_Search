from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic evolves the previous best version by further increasing the penalties
    for difficult-to-resolve patterns, capitalizing on the available headroom in the cost_ratio
    (1.612 vs 1.80 limit) to further reduce the number of generated nodes.

    The successful formula combining Manhattan Distance (MD), Linear Conflicts (LC), and
    Corner Conflicts (CC) is retained, but with more aggressive weighting:

    1. Increased Linear Conflict Weight: The penalty multiplier for linear conflicts
       is increased from 3 to 4 (`lc * 4`). This heavily penalizes states where tiles are
       in their correct row/column but in the wrong order, as this was the most
       impactful term in prior improvements.

    2. Increased Overall Weight: The final greedy weighting factor is increased from 2.7
       to 2.8. This makes the A* search more focused, aiming to prune more branches
       of the search tree by inflating the heuristic value across the board.

    The combination of a higher base penalty for linear conflicts and a higher overall
    weight is designed to aggressively reduce the search space while keeping the solution
    quality within the required bounds.
    """
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

    md = 0
    for i, val in enumerate(tiles):
        if val != 0:
            md += MD_TABLE[i][val]

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

    # Base heuristic with an increased penalty for linear conflicts (lc * 4).
    base_h = md + lc * 4 + cc

    # Increased overall weight to make the search more greedy.
    return int(base_h * 2.8)