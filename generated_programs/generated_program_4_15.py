from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic builds upon the best-performing prior versions by cautiously increasing
    the greedy multiplier. The core of the heuristic remains the potent combination of
    Manhattan Distance (MD), heavily weighted Linear Conflicts (LC), and Corner Conflicts (CC).

    Analysis of previous versions shows a clear trend: increasing the final
    weighting factor consistently improves the score (by reducing generated nodes), as
    long as the solution quality (`cost_ratio`) remains within the 1.80 limit. The
    last successful version used a multiplier of 3.5 and achieved the top score.

    This version takes a small, incremental step to further optimize performance:

    1.  Retained Core Logic: The base heuristic `md + lc * 5 + cc` is kept
        intact. The `lc * 5` term provides a massive penalty for difficult-to-resolve
        linear conflicts, and the `cc` term correctly identifies blocking corner tiles.
        This base has proven extremely effective.

    2.  Increased Greediness: The final multiplier is increased from 3.5 to 3.6.
        This change aims to prune even more nodes from the A* search tree. It is a
        calculated risk, leveraging the remaining headroom in the `cost_ratio`
        to achieve a better `generated_ratio`. The small increment is intended to
        keep the solution quality safely within the required bounds while pushing for a
        new best score.
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
    # Check if corner tiles are in place but are blocking other tiles.
    # Top-right corner (tile 3 at index 3)
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        cc += 2
    # Bottom-left corner (tile 12 at index 12)
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        cc += 2
    # Bottom-right corner (tile 15 at index 15)
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        cc += 2

    base_h = md + lc * 5 + cc

    # Increment the multiplier from 3.5 to 3.6 to be slightly more greedy.
    return int(base_h * 3.6)