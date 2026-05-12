from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic further enhances the previous version by increasing the penalty for corner conflicts.
    It builds upon the successful combination of Manhattan distance (MD), linear conflicts (LC),
    and corner conflicts (CC) by applying a stronger weight specifically to the CC component.

    - MD_TABLE: Precomputed Manhattan distances for efficiency.
    - GOAL_R, GOAL_C: Precomputed goal rows and columns.

    - Manhattan Distance (md): Calculated for all non-blank tiles.

    - Linear Conflicts (lc):
        - The calculation iterates directly through tile positions using nested loops for efficiency.
        - A pair of tiles are in a linear conflict if they are in their goal row/column
          but are in the wrong order relative to each other. Each conflict adds 2 to `lc`.
        - The linear conflict component (`lc`) is tripled within the base heuristic calculation
          (`base_h = md + lc * 3 + cc * 2`).

    - Corner Conflicts (cc):
        - Specific conflicts for tiles 3, 12, 15 if they are in their goal position
          but block an adjacent tile from reaching its goal position. Each conflict adds 2 to `cc`.
        - The corner conflict component (`cc`) is now doubled (`cc * 2`) within the base heuristic calculation.
          This selectively increases the heuristic for states with these difficult-to-resolve patterns,
          guiding A* more effectively away from them.

    - Final Weighting: The overall weighting of 2.7 is maintained. The targeted increase in the
      `cc` component should further reduce generated nodes without drastically increasing the
      solution cost ratio beyond the 1.80 bound, given the previous comfortable margin.
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
    # Top-right corner (tile 3 at pos 3)
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        cc += 2
    # Bottom-left corner (tile 12 at pos 12)
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        cc += 2
    # Bottom-right corner (tile 15 at pos 15)
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        cc += 2

    # Base heuristic with an increased penalty for linear conflicts (lc * 3)
    # and now for corner conflicts (cc * 2).
    base_h = md + lc * 3 + cc * 2

    # Apply a high weight to make the search more greedy.
    return int(base_h * 2.7)