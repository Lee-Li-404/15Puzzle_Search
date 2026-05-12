from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic builds upon the successful formula of combining Manhattan Distance (MD),
    weighted Linear Conflicts (LC), and specific pattern penalties. The evolution focuses
    on making the heuristic significantly more aggressive to minimize generated nodes, 
    capitalizing on the available headroom below the 1.80 cost_ratio limit.

    Key Improvements:
    1.  Increased Overall Greediness: The final WEIGHT_FACTOR is pushed from 3.65 to 3.85,
        the most significant change to drive down node generation.
    2.  Amplified Linear Conflict Penalty: The multiplier for LC is increased from 6.0 to 6.5,
        further penalizing tiles that are in their correct row/column but in the wrong order.
    3.  Strengthened Pattern Penalties: All existing pattern penalties (corner conflicts and
        specific swaps) have been increased to give them more influence on the heuristic value.
    4.  Expanded Pattern Detection: Two new, common, and hard-to-resolve swap patterns have
        been added: the left-column swap (4,8) and the final-tile swap (14,15).
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
    # Corner Conflicts: Increased penalty for a corner tile blocking its neighbors.
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        patterns += 3
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        patterns += 3
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        patterns += 3

    # Swap Conflicts: Increased penalties and new patterns for specific swaps.
    if tiles[1] == 4 and tiles[4] == 1: # L-shape swap
        patterns += 7
    if tiles[1] == 2 and tiles[2] == 1: # Top row swap
        patterns += 5
    if tiles[13] == 14 and tiles[14] == 13: # Last row swap
        patterns += 5
    if tiles[14] == 15 and tiles[15] == 14: # Last two tiles swap (new)
        patterns += 5
    if tiles[7] == 11 and tiles[11] == 7: # Right column swap
        patterns += 5
    if tiles[4] == 8 and tiles[8] == 4: # Left column swap (new)
        patterns += 5

    base_h = md + lc * 6.5 + patterns

    WEIGHT_FACTOR = 3.85
    return int(base_h * WEIGHT_FACTOR)