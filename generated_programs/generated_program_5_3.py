from fifteen_state_class import State

def heuristic(s: State) -> int:
    """An improved heuristic based on Manhattan distance and linear conflicts, with an increased weight.

    This heuristic function calculates the sum of Manhattan distances (MD) for all tiles
    and adds a penalty for linear conflicts (LC). The total is then multiplied by a weight
    to make the A* search greedier, aiming to reduce the number of generated nodes.

    - Manhattan Distance (MD): Pre-calculated in a lookup table for efficiency.
    - Linear Conflicts (LC): A pair of tiles are in a linear conflict if they are in their
      goal row/column but are in the wrong order relative to each other. Each conflict
      adds 2 to the heuristic value.
    - Weighting: The combined heuristic (MD + LC) is multiplied by a weight of 2.4. The
      previous best version used 1.8, but its worst-case cost ratio (1.250) was well
      below the 1.80 limit. Increasing the weight makes the search more aggressive,
      reducing node expansions while aiming to keep the solution cost within bounds.
    """
    # Lookup table for Manhattan Distance. MD_TABLE[i][val] is the distance
    # for a tile with value 'val' at position 'i' to its goal.
    MD_TABLE = tuple(
        tuple(
            abs((i // 4) - (val // 4)) + abs((i % 4) - (val % 4))
            for val in range(16)
        )
        for i in range(16)
    )
    
    # Lookup tables for the goal row and column of each tile value.
    # This avoids repeated division and modulo operations in the loops.
    GOAL_R = tuple(val // 4 for val in range(16))
    GOAL_C = tuple(val % 4 for val in range(16))

    tiles = s.tiles
    
    # Calculate Manhattan Distance for all non-blank tiles.
    md = 0
    for i, val in enumerate(tiles):
        if val != 0:
            md += MD_TABLE[i][val]

    # Calculate Linear Conflicts.
    lc = 0
    # Row conflicts: Check every pair of tiles in each row.
    for r in range(4):
        for c1 in range(4):
            val1 = tiles[r * 4 + c1]
            # A tile can only be in conflict if it's in its goal row.
            if val1 == 0 or GOAL_R[val1] != r:
                continue
            for c2 in range(c1 + 1, 4):
                val2 = tiles[r * 4 + c2]
                # If val2 is also in its goal row and the pair is inverted, it's a conflict.
                if val2 != 0 and GOAL_R[val2] == r and val1 > val2:
                    lc += 2

    # Column conflicts: Check every pair of tiles in each column.
    for c in range(4):
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            # A tile can only be in conflict if it's in its goal column.
            if val1 == 0 or GOAL_C[val1] != c:
                continue
            for r2 in range(r1 + 1, 4):
                val2 = tiles[r2 * 4 + c]
                # If val2 is also in its goal col and the pair is inverted, it's a conflict.
                if val2 != 0 and GOAL_C[val2] == c and GOAL_R[val1] > GOAL_R[val2]:
                    lc += 2

    # Combine the admissible heuristic (md + lc) and apply a weight.
    # The weight is increased to 2.4 to prioritize reducing generated nodes.
    total_h = md + lc
    return int(total_h * 2.4)