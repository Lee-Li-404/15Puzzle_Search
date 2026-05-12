from fifteen_state_class import State

def heuristic(s: State) -> int:
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
    blank_idx = -1
    for i, val in enumerate(tiles):
        if val != 0:
            md += MD_TABLE[i][val]
        else:
            blank_idx = i # Store blank tile's current position

    lc = 0
    # Row conflicts
    for r in range(4):
        for c1 in range(4):
            val1 = tiles[r * 4 + c1]
            # Only consider tiles that belong in this row in the goal state and are not the blank tile.
            if val1 == 0 or GOAL_R[val1] != r:
                continue
            for c2 in range(c1 + 1, 4):
                val2 = tiles[r * 4 + c2]
                # Check for a linear conflict: two tiles are in their goal row
                # but are in reverse order relative to their goal columns.
                if val2 != 0 and GOAL_R[val2] == r and GOAL_C[val1] > GOAL_C[val2]:
                    lc += 2 # Add 2 for each conflict as per standard linear conflicts heuristic

    # Column conflicts
    for c in range(4):
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            # Only consider tiles that belong in this column in the goal state and are not the blank tile.
            if val1 == 0 or GOAL_C[val1] != c:
                continue
            for r2 in range(r1 + 1, 4):
                val2 = tiles[r2 * 4 + c]
                # Check for a linear conflict: two tiles are in their goal column
                # but are in reverse order relative to their goal rows.
                if val2 != 0 and GOAL_C[val2] == c and GOAL_R[val1] > GOAL_R[val2]:
                    lc += 2 # Add 2 for each conflict

    cc = 0
    # Corner conflicts: penalize specific corner tiles that are correctly placed
    # but are 'locking' their neighbors out of position, making them hard to move.
    # Top-right corner (tile 3 at index 3)
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        cc += 2
    # Bottom-left corner (tile 12 at index 12)
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        cc += 2
    # Bottom-right corner (tile 15 at index 15)
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        cc += 2

    # Calculate the Manhattan distance of the blank tile (0) from its goal position (index 0).
    # The goal is to have tile 0 at the top-left corner (row 0, col 0).
    blank_md = (blank_idx // 4) + (blank_idx % 4)

    # Combine Manhattan Distance, weighted Linear Conflicts, Corner Conflicts, and a penalty for blank tile position.
    # The weights are tuned to be aggressive in reducing generated nodes while staying within cost_ratio limits.
    # The linear conflicts weight is slightly increased from the previous best, and a small blank_md penalty is added.
    base_h = md + lc * 6.25 + cc + blank_md * 0.5

    # Apply an overall greedy multiplier to further inflate the heuristic estimate.
    # This helps A* prune the search tree more aggressively.
    return int(base_h * 3.0)