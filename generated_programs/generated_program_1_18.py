from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic focuses on maximizing node generation reduction by 
    significantly increasing the aggressiveness of the Manhattan Distance (MD) 
    and Linear Conflicts (LC) components, alongside carefully chosen pattern 
    penalties. It leverages the substantial headroom in the cost_ratio 
    (currently 1.612 vs 1.80 limit) to make the A* search highly greedy.

    Key aggressive adjustments:
    1.  **MD Table Lookup**: Pre-calculates Manhattan distances for O(1) lookup per tile.
    2.  **Aggressive Linear Conflict Weighting**: The multiplier for linear conflicts 
        (lc) is set to 8.0. This heavily penalizes any tile in its correct 
        row/column but in the wrong order, promoting faster resolution of these 
        problematic states.
    3.  **Increased Base Weight**: The overall `WEIGHT_FACTOR` is boosted to 4.0. 
        This inflates the total heuristic value significantly, driving down the 
        number of generated nodes by making A* more prone to prune branches.
    4.  **Targeted Pattern Penalties**: A few high-impact, local patterns are 
        identified and penalized. These are specific tile swaps that often 
        lead to local minima or require many moves to resolve.

    The goal is to push `generated_ratio` as low as possible while ensuring 
    `cost_ratio` remains ≤ 1.80. The combination of these aggressive measures 
    aims for a dominant reduction in node generation.
    """
    MD_TABLE = (
        (
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

    # Pattern penalties - focusing on specific problematic swaps
    patterns = 0
    
    # Top-left 2x2 block issues:
    # If tile 1 is 4 and tile 4 is 1, they are swapped. High penalty.
    if tiles[1] == 4 and tiles[4] == 1:
        patterns += 6
    # If tiles 2 and 5 are swapped.
    if tiles[2] == 5 and tiles[5] == 2:
        patterns += 5
    
    # Right edge issues:
    # If tiles 7 and 11 are swapped.
    if tiles[7] == 11 and tiles[11] == 7:
        patterns += 5
    
    # Bottom edge issues:
    # If tiles 13 and 14 are swapped.
    if tiles[13] == 14 and tiles[14] == 13:
        patterns += 5
    # If tiles 14 and 15 are swapped.
    if tiles[14] == 15 and tiles[15] == 14:
        patterns += 5

    # A highly aggressive base heuristic: MD + very heavily weighted LC + patterns
    # The LC multiplier is pushed to 8.0 to maximize pruning.
    base_h = md + lc * 8.0 + patterns

    # The final overall greedy multiplier is increased to 4.0.
    WEIGHT_FACTOR = 4.0
    return int(base_h * WEIGHT_FACTOR)