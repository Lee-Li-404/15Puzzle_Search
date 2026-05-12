from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic evolves the previous best versions by adopting a more aggressive
    weighting strategy and incorporating an additional key pattern penalty. The goal
    is to leverage the existing cost_ratio headroom to drastically reduce the number
    of generated nodes.

    Key enhancements:
    1.  Increased Overall Weighting: The main `WEIGHT_FACTOR` is raised from 3.65 to 3.8.
        This is the most direct and powerful change to make the A* search greedier,
        pruning more of the search space.
    2.  Added 'Last Two Tiles' Pattern: A specific penalty is added for the case
        where the last two tiles (14 and 15) are swapped. This is a common and costly
        final configuration that linear conflicts alone may not sufficiently penalize.
    3.  Retained Core Strengths: The highly effective structure of combining Manhattan
        Distance (MD), heavily weighted Linear Conflicts (LC * 6), corner conflicts, and
        other specific swap penalties is maintained, as it forms a robust foundation.

    The combination of a higher global weight and a more refined set of pattern
    penalties aims for a new low in the generated_ratio while keeping the cost_ratio
    safely under the 1.80 limit.
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
    # Corner Conflicts: A corner tile is in place, blocking its neighbors.
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        patterns += 2
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        patterns += 2
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        patterns += 2

    # Swap Conflicts: Penalize specific, high-cost swaps extra.
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

    # The base heuristic combines MD, heavily weighted LC, and pattern penalties.
    base_h = md + lc * 6 + patterns

    # Final overall greedy multiplier, increased to push down generated nodes.
    WEIGHT_FACTOR = 3.8
    return int(base_h * WEIGHT_FACTOR)