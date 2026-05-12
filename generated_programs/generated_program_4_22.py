from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic continues the successful evolutionary strategy of aggressively
    penalizing linear conflicts (LC) to prune the A* search tree more effectively.
    Building upon the previous best versions, which saw consistent improvement by
    incrementing the LC weight, this iteration takes the next logical step.

    Key Change:
    1.  Increased Linear Conflict Weight: The multiplier for the linear conflict
        term is raised from 10 to 11. This makes the heuristic even more sensitive
        to these particularly difficult arrangements, aiming to steer the search
        away from them earlier and thus reduce the total number of generated nodes.

    The overall greedy multiplier of 3.6 is maintained, as it has proven to be a
    robust factor in balancing search space reduction with solution quality.
    This targeted increase in the LC penalty is expected to further improve the
    `generated_ratio` while remaining safely within the `cost_ratio` limit.
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

    md = 0  # Manhattan Distance
    for i, val in enumerate(tiles):
        if val != 0:
            md += MD_TABLE[i][val]

    lc = 0  # Linear Conflicts
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

    cc = 0  # Corner Conflicts
    # Top-right corner (tile 3 at index 3)
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        cc += 2
    # Bottom-left corner (tile 12 at index 12)
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        cc += 2
    # Bottom-right corner (tile 15 at index 15)
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        cc += 2

    # Incrementing the linear conflict weight from 10 to 11.
    base_h = md + lc * 11 + cc

    # The overall greedy multiplier is maintained at 3.6.
    return int(base_h * 3.6)