from fifteen_state_class import State

def heuristic(s: State) -> int:
    GOAL_R = (0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3)
    GOAL_C = (0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3)

    tiles = s.tiles

    # Manhattan Distance (MD)
    md = 0
    for i, val in enumerate(tiles):
        if val != 0:
            cur_r, cur_c = divmod(i, 4)
            md += abs(GOAL_R[val] - cur_r) + abs(GOAL_C[val] - cur_c)

    # Linear Conflicts (LC)
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

    # Corner Conflicts (CC)
    # Penalize specific corner tiles that are in place but are 'locked' by misaligned neighbors.
    cc = 0
    # Top-right corner (position 3, which is goal for tile 3)
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        cc += 1
    # Bottom-left corner (position 12, which is goal for tile 12)
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        cc += 1
    # Bottom-right corner (position 15, which is goal for tile 15)
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        cc += 1

    # Weighting strategy:
    # The previous best heuristic (heuristic_v1) achieved score=0.0006 with cost_ratio=1.776,
    # using (MD + 3.5 * LC) * 3.2. This indicated that a higher overall multiplier (3.2)
    # was effective, even without explicit corner conflict handling.
    # Other attempts (heuristic_prev1) included CC but with a lower overall multiplier (3.1)
    # which resulted in a worse score (0.0008).
    # This version aims to combine the strength of heuristic_v1's overall multiplier with
    # the enhanced pattern recognition of Corner Conflicts.
    # We retain the core `MD + 3.5 * LC` structure and its `3.2` overall multiplier,
    # then add a small, carefully weighted `CC` component to guide the search in specific
    # challenging states without excessively increasing the heuristic value.

    conflict_weight_LC = 3.5
    conflict_weight_CC = 0.5 # A small weight for CC to provide gentle guidance
    overall_weight = 3.2

    base_h = md + conflict_weight_LC * lc + conflict_weight_CC * cc

    return int(base_h * overall_weight)