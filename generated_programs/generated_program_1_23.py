from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic refines previous versions by balancing increased greediness
    with targeted pattern recognition to reduce generated nodes while maintaining
    cost_ratio within bounds.

    Key enhancements:
    1.  Linear Conflict Weight: The linear conflict (LC) multiplier is set to 5.5.
        This is a moderate increase from 5.0 (heuristic_v1) but less aggressive
        than 6.1 (heuristic_prev1). It enhances the penalty for tiles in their
        goal row/column but out of order, a known factor for search depth.

    2.  Refined Pattern Penalties: Specific patterns known to be bottlenecks or
        require many moves are penalized:
        - Corner Conflicts: Penalty for a corner tile being in place while its
          immediate neighbors are not. Increased from 2 (in heuristic_v1) to 3
          for each such corner.
        - Specific Tile Swaps: Penalties for common difficult swaps (e.g., L-shape
          swap 1<->4, top row 1<->2, last row 13<->14, right column 7<->11, last
          two 14<->15). These penalties (3-4) are slightly less aggressive than
          in heuristic_prev1 (4-5), aiming for a better balance between pruning
          and solution cost.

    3.  Overall Weighting Factor: The final global multiplier is increased from 2.9
        (in heuristic_v1) to 3.0. This makes the A* search slightly more greedy
        overall, encouraging quicker convergence by inflating heuristic values.

    This approach aims to further reduce the 'generated_ratio' by leveraging more
    specific pattern knowledge and slightly higher base weights, without risking a
    'cost_ratio' breach beyond 1.80.
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
    # Corner Conflicts: Penalties for a corner tile blocking its neighbors.
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        patterns += 3
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        patterns += 3
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        patterns += 3

    # Swap Conflicts: Penalize specific, high-cost swaps.
    if tiles[1] == 4 and tiles[4] == 1: # L-shape swap (1<->4)
        patterns += 4
    if tiles[1] == 2 and tiles[2] == 1: # Top row swap (1<->2)
        patterns += 3
    if tiles[13] == 14 and tiles[14] == 13: # Last row swap (13<->14)
        patterns += 3
    if tiles[7] == 11 and tiles[11] == 7: # Right column swap (7<->11)
        patterns += 3
    if tiles[14] == 15 and tiles[15] == 14: # Last two tiles swap (14<->15)
        patterns += 3

    # The base heuristic combines MD, a moderately higher weighted LC, and refined pattern penalties.
    base_h = md + lc * 5.5 + patterns

    # Final overall greedy multiplier.
    WEIGHT_FACTOR = 3.0
    return int(base_h * WEIGHT_FACTOR)
