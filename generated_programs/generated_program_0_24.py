from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic evolves the best previous versions by synthesizing their strongest
    components and introducing a more robust formulation. The goal is to provide
    more nuanced guidance to A*, especially for hard-to-resolve configurations,
    to further reduce generated nodes while staying within the cost_ratio limit.

    Key improvements:
    1. Weighted Manhattan Distance (WMD): A 5% weight is added to the MD of
       tiles belonging to the bottom two rows, prioritizing harder-to-place tiles.
    2. Corrected Linear Conflicts (LC): Each conflict now adds a penalty of 2,
       correctly reflecting the minimum moves needed for resolution. This is more
       theoretically sound than adding 1.
    3. Corner Conflicts (CC): A penalty is added if a corner tile is in its
       final position but blocks its adjacent tiles, targeting tricky "last moves"
       scenarios.
    4. Re-balanced Weighting: With new components and a stronger LC formulation,
       the weights are carefully re-calibrated. The effective weights for LC and
       the new CC term are tuned to match the aggressiveness of prior best-performing
       heuristics, while the overall greedy multiplier is adjusted to keep the
       solution quality high (low cost_ratio).
    """
    GOAL_R = tuple(val // 4 for val in range(16))
    GOAL_C = tuple(val % 4 for val in range(16))

    tiles = s.tiles
    wmd = 0.0

    for i, val in enumerate(tiles):
        if val == 0:
            continue

        goal_r = GOAL_R[val]
        dist = abs(goal_r - (i // 4)) + abs(GOAL_C[val] - (i % 4))

        if goal_r >= 2:
            wmd += dist * 1.05
        else:
            wmd += dist

    lc = 0
    for r in range(4):
        for c1 in range(4):
            val1 = tiles[r * 4 + c1]
            if val1 == 0 or GOAL_R[val1] != r:
                continue
            for c2 in range(c1 + 1, 4):
                val2 = tiles[r * 4 + c2]
                if val2 != 0 and GOAL_R[val2] == r and val1 > val2:
                    lc += 2

    for c in range(4):
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            if val1 == 0 or GOAL_C[val1] != c:
                continue
            for r2 in range(r1 + 1, 4):
                val2 = tiles[r2 * 4 + c]
                if val2 != 0 and GOAL_C[val2] == c and val1 > val2:
                    lc += 2

    cc = 0
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        cc += 2
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        cc += 2
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        cc += 2

    conflict_weight = 1.875
    overall_weight = 3.0

    base_heuristic = wmd + conflict_weight * (lc + cc)

    return int(base_heuristic * overall_weight)