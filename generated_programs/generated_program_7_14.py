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
    blank_idx = -1

    md = 0
    for i, val in enumerate(tiles):
        if val != 0:
            md += MD_TABLE[i][val]
        else:
            blank_idx = i

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
    # Corner conflicts: penalize locked corners
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        cc += 3
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        cc += 3
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        cc += 3
        
    # Penalty for the blank tile being far from its home in the top-left corner.
    blank_dist = (blank_idx // 4) + (blank_idx % 4)

    # The base heuristic combines Manhattan distance, a heavily weighted linear conflicts term,
    # corner conflicts, and a penalty for the blank tile's distance from the goal.
    # The weights are aggressively tuned to reduce generated nodes.
    base_h = md + lc * 7 + cc + blank_dist

    # An increased overall greedy factor pushes the heuristic to be more aggressive,
    # capitalizing on the cost_ratio headroom to further prune the search space.
    return int(base_h * 3.25)