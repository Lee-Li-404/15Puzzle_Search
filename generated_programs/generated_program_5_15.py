from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic aims to further reduce the number of generated nodes by leveraging
    an aggressive combination of Manhattan Distance (MD), Linear Conflicts (LC),
    and Corner Conflicts (CC), with increased weights based on observed performance
    of previous versions, specifically the one that achieved a score of 0.0006.

    It retains the robust and efficient precomputation of MD_TABLE, GOAL_R, and GOAL_C.

    Key adjustments and rationale:
    1.  Manhattan Distance (MD): Standard calculation, serving as the admissible base.
    2.  Linear Conflicts (LC):
        - The detection logic for linear conflicts (tiles in their goal row/column but out of order)
          is carefully maintained for correctness. For column conflicts, this involves comparing
          the *goal rows* of the tiles, not their numerical values, to accurately identify conflicts.
        - The multiplier for linear conflicts is set to 6 (`lc * 6`). This high weight for LC has
          proven very effective in previous iterations to penalize complex inversions that require
          many moves to resolve, thus guiding the search more aggressively.
    3.  Corner Conflicts (CC):
        - Specific corner cases (tiles 3, 12, 15) are checked if they are in their correct corner
          but blocking an adjacent tile that also belongs in an adjacent corner-related position.
        - The penalty for corner conflicts remains at a base of 2 per conflict (`cc`).
    4.  Overall Greedy Multiplier: The entire sum (`md + lc * 6 + cc`) is multiplied by 3.2.
        This significant inflation of the heuristic value makes A* more greedy, pruning
        substantially more nodes while aiming to keep the `cost_ratio` below the 1.80 bound,
        as suggested by the strong performance (score 0.0006) of a prior version with these weights.

    The objective is to achieve a lower `generated_ratio` by aggressively guiding the A* search
    while maintaining the `cost_ratio` constraint.
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
            if val1 != 0 and GOAL_R[val1] == r:
                for c2 in range(c1 + 1, 4):
                    val2 = tiles[r * 4 + c2]
                    if val2 != 0 and GOAL_R[val2] == r and val1 > val2:
                        lc += 2
    # Column conflicts
    for c in range(4):
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            if val1 != 0 and GOAL_C[val1] == c:
                for r2 in range(r1 + 1, 4):
                    val2 = tiles[r2 * 4 + c]
                    if val2 != 0 and GOAL_C[val2] == c and GOAL_R[val1] > GOAL_R[val2]:
                        lc += 2

    cc = 0
    # Corner Conflicts: specific tiles in place blocking others
    # Top-right corner (tile 3 at pos 3)
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        cc += 2
    # Bottom-left corner (tile 12 at pos 12)
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        cc += 2
    # Bottom-right corner (tile 15 at pos 15)
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        cc += 2

    base_h = md + lc * 6 + cc

    return int(base_h * 3.2)
