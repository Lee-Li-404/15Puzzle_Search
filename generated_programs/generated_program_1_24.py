from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic synthesizes the most effective components from previous top-performing
    versions to further reduce the number of generated nodes. It is an evolution
    of the 'vr0' heuristic (score=0.0007).

    Key Enhancements:
    1.  **Comprehensive Pattern Set**: Incorporates the most complete set of known
        difficult patterns from prior versions. This includes three corner-lock
        scenarios and five specific high-cost tile swaps (such as the L-shape
        1<->4 swap and the last-two-tiles 14<->15 swap).

    2.  **Aggressive but Proven Weighting**: It retains the highly effective Linear
        Conflict weight of 6.0 from 'vr0'. The final overall greedy multiplier is
        incrementally increased from 3.75 to 3.8. This small increase in
        aggressiveness aims to prune more of the search tree, capitalizing on the
        cost_ratio headroom observed in previous best heuristics.

    3.  **Balanced Penalties**: While the set of recognized patterns is expanded,
        the penalty values for each pattern are kept at the moderate levels that
        proved successful in 'vr0' (e.g., +2 for corner locks, +4/+5 for swaps),
        avoiding overly severe penalties that might mislead the search.

    This approach is a carefully calculated push for higher performance by combining
    a more complete problem representation (more patterns) with a slightly more
    aggressive search strategy (higher overall weight).
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

    patterns = 0
    # Corner Conflicts: A solved corner tile blocking its neighbors.
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        patterns += 2
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        patterns += 2
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        patterns += 2

    # Swap Conflicts: Penalize specific, high-cost swaps.
    if tiles[1] == 4 and tiles[4] == 1: # L-shape swap
        patterns += 5
    if tiles[1] == 2 and tiles[2] == 1: # Top row swap
        patterns += 4
    if tiles[13] == 14 and tiles[14] == 13: # Last row swap
        patterns += 4
    if tiles[7] == 11 and tiles[11] == 7: # Right column swap
        patterns += 4
    if tiles[14] == 15 and tiles[15] == 14: # Last two tiles swap
        patterns += 4

    base_h = md + lc * 6.0 + patterns

    WEIGHT_FACTOR = 3.8
    return int(base_h * WEIGHT_FACTOR)