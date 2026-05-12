from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic improves upon the best-performing predecessors by synthesizing
    their most effective components and introducing a more robust logic.

    1.  Robust Linear Conflicts: It adopts the more accurate linear conflict
        detection logic which correctly compares goal rows for column conflicts, 
        making it more accurate than predecessors that used a simple value comparison.

    2.  Corner Conflict Integration: It incorporates the "Corner Conflict" (CC)
        penalty, a pattern-based heuristic that penalizes tiles locked in corners
        without their neighbors in place. This adds another layer of intelligence
        to guide the search away from known difficult-to-resolve states.

    3.  Rebalanced Weighting: To accommodate the new CC term and the refined LC
        logic without exceeding the cost_ratio limit of 1.80, the weights are
        carefully rebalanced. The formula `(MD + 3.5*LC + 2.0*CC) * 3.1`
        maintains a strong Manhattan Distance (MD) component, a significant
        Linear Conflict (LC) penalty, and a meaningful CC penalty. This blend
        aims to create a more informed heuristic value, pruning the search tree
        more effectively than a simple greedy increase in weight.
    """
    GOAL_R = (0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3)
    GOAL_C = (0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3)

    tiles = s.tiles

    md = 0
    for i, val in enumerate(tiles):
        if val != 0:
            md += abs(GOAL_R[val] - (i // 4)) + abs(GOAL_C[val] - (i % 4))

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
                    lc += 1
    # Column conflicts
    for c in range(4):
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            if val1 == 0 or GOAL_C[val1] != c:
                continue
            for r2 in range(r1 + 1, 4):
                val2 = tiles[r2 * 4 + c]
                if val2 != 0 and GOAL_C[val2] == c and GOAL_R[val1] > GOAL_R[val2]:
                    lc += 1

    cc = 0
    # Top-right corner (tile 3)
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        cc += 1
    # Bottom-left corner (tile 12)
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        cc += 1
    # Bottom-right corner (tile 15)
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        cc += 1

    base_h = md + 3.5 * lc + 2.0 * cc
    
    return int(base_h * 3.1)