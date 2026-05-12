from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic aggressively boosts Manhattan Distance (MD) and Linear Conflicts (LC)
    with a high overall multiplier to minimize generated nodes. It builds upon previous
    successes by finding a balance between high greediness and maintaining a low cost_ratio.

    Key elements:
    1.  **MD Lookup Table**: Efficient O(1) lookup for Manhattan distances.
    2.  **Aggressive Linear Conflicts**: LC is weighted by 7.0. This significantly penalizes
        tiles in their correct row/column but in the wrong order, as this is a key factor
        in search complexity.
    3.  **Pattern Penalties**: Specific, high-cost swap patterns are identified and penalized.
        These are critical for pruning states that often lead to long solution paths.
        - Top-left 2x2 block swaps (1<->4, 2<->5)
        - Right edge swaps (7<->11)
        - Bottom edge swaps (13<->14, 14<->15)
    4.  **High Overall Weighting**: A WEIGHT_FACTOR of 3.9 is used. This significantly inflates
        the heuristic value, making the A* search more greedy and likely to prune branches,
        thus reducing the number of unique nodes generated. This factor is chosen to push
        generated_ratio lower while staying within the cost_ratio <= 1.80 bound.

    The aim is to achieve a very low `generated_ratio` by making the heuristic highly greedy,
    while ensuring `cost_ratio` remains within the acceptable limit.
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
    # The LC multiplier is pushed to 7.0 to maximize pruning.
    base_h = md + lc * 7.0 + patterns

    # The final overall greedy multiplier is increased to 3.9.
    WEIGHT_FACTOR = 3.9
    return int(base_h * WEIGHT_FACTOR)
