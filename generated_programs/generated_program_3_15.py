from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic evolves the best-performing previous versions (score=0.0006) by
    introducing a more aggressive penalty structure. The goal is to leverage the
    remaining headroom in the cost_ratio bound (<= 1.80) to achieve a significant
    reduction in the number of unique nodes generated.

    The core strategy retains the successful combination of Manhattan Distance (MD),
    Linear Conflicts (LC), and Corner Conflicts (CC), but with refined weights:

    1.  Increased Corner Conflict Penalty: The penalty for a corner tile being in
        its correct position but blocking its neighbors is doubled from 2 to 4.
        These "locked corner" states are particularly difficult to resolve and
        warrant a much stronger penalty to guide the search away from them early.

    2.  Aggressive Linear Conflict Weight: The multiplier for linear conflicts
        remains at the highly effective value of 6 (`lc * 6`). This term is crucial
        for identifying states that require many moves to untangle.

    3.  Increased Overall Greedy Weight: The final weighting factor is pushed from
        3.4 to 3.5. This small but critical increase makes the entire heuristic
        greedier, further prioritizing states that appear closer to the goal and
        pruning more of the search tree.

    The resulting heuristic is calculated as: `int((MD + LC * 6 + CC) * 3.5)`,
    where CC incorporates the new, higher penalty of 4 for each corner conflict.
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
    # Increased penalty for Corner Conflicts to more aggressively avoid these states.
    CORNER_PENALTY = 4
    # Top-right corner (tile 3)
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        cc += CORNER_PENALTY
    # Bottom-left corner (tile 12)
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        cc += CORNER_PENALTY
    # Bottom-right corner (tile 15)
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        cc += CORNER_PENALTY

    # Combine all components. Linear conflicts are weighted heavily (lc * 6).
    base_h = md + lc * 6 + cc

    # Apply an even more aggressive overall greedy weighting factor (increased from 3.4 to 3.5).
    return int(base_h * 3.5)