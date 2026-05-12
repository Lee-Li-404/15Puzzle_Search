from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic evolves the successful formula of its predecessors by placing a
    stronger, more targeted emphasis on resolving known difficult board configurations,
    particularly "corner locks."

    Key enhancements:
    1.  **Strengthened Corner Conflict Penalty**: The penalty for a solved corner tile
        blocking its unsolved neighbors (at positions 3, 12, and 15) is doubled
        from 2 to 4. This aggressively discourages states that are known to be
        local minima and costly to escape.
    2.  **Refined Linear Conflict Weight**: The linear conflict (LC) multiplier is
        incrementally increased from 6.0 to 6.1. LC is a powerful component, and this
        slight boost enhances its influence without drastically risking an increase
        in solution cost.
    3.  **Stable High-Performance Core**: The heuristic maintains the proven structure
        of combining Manhattan Distance (MD), heavily weighted LC, specific swap
        penalties (e.g., the 1<->4 L-shape), and a high overall greedy multiplier (3.8).

    This approach focuses on making the heuristic more informed about specific hard
    patterns, aiming to reduce the search space more intelligently than simply
    increasing the global weight, thereby pushing for a lower generated_ratio while
    maintaining the cost_ratio within bounds.
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
        patterns += 4
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        patterns += 4
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        patterns += 4

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

    # The base heuristic combines MD, a slightly higher weighted LC, and stronger pattern penalties.
    base_h = md + lc * 6.1 + patterns

    # Final overall greedy multiplier, kept at a proven high level.
    WEIGHT_FACTOR = 3.8
    return int(base_h * WEIGHT_FACTOR)