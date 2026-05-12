from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic evolves from the top-performing prior versions (score=0.0006),
    which demonstrated that an aggressive, weighted combination of Manhattan
    Distance (MD), Linear Conflicts (LC), and Corner Conflicts (CC) is highly
    effective at reducing the search space.

    The strategy is to further increase the heuristic's greediness by tuning the
    weights, based on the success of `heuristic_prev1` (lc_weight=7, overall=3.3).
    The goal is to generate even fewer unique nodes while staying within the
    cost_ratio bound.

    Key Adjustments:
    1.  Increased Linear Conflict Weight: The penalty for linear conflicts is raised
        from 7 to 7.5. LC is a very strong signal of puzzle difficulty, and
        amplifying its contribution steers the search more decisively away from
        these hard-to-resolve subproblems.

    2.  Increased Overall Multiplier: The final greedy multiplier is increased from
        3.3 to 3.4. This uniformly inflates the heuristic value, making the A*
        search more focused and enhancing its pruning power across the entire
        search tree.

    This combination of more aggressive, fine-tuned weights is designed to push
    the limits of greediness to achieve a new low in generated nodes.
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
    # Row conflicts: tiles in their goal row but reversed relative to each other.
    for r in range(4):
        for c1 in range(4):
            val1 = tiles[r * 4 + c1]
            if val1 == 0 or GOAL_R[val1] != r:
                continue
            for c2 in range(c1 + 1, 4):
                val2 = tiles[r * 4 + c2]
                if val2 != 0 and GOAL_R[val2] == r and val1 > val2:
                    lc += 2
    # Column conflicts: tiles in their goal column but reversed relative to each other.
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
    # Specific corner tiles that are "stuck", blocking adjacent goal positions.
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        cc += 2
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        cc += 2
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        cc += 2

    # Combine components with highly aggressive weights.
    # Using (lc * 15) // 2 is an integer-safe way to multiply by 7.5.
    base_h = md + (lc * 15) // 2 + cc

    return int(base_h * 3.4)
