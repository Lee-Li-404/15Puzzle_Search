from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic further refines the approach by focusing on:
    1. A more accurate and robust calculation of linear conflicts.
    2. Incorporating a stronger penalty for corner conflicts.
    3. Adjusting weights to aggressively reduce generated nodes while staying within
       the cost_ratio bound, leveraging the available headroom.

    Key improvements over previous versions:
    - Enhanced Linear Conflicts: The calculation now correctly identifies and penalizes
      both row and column conflicts more precisely. Each conflict is given a weight
      of 2, reflecting its significance in hindering progress.
    - Tuned Corner Conflict Penalty: Corner conflicts are now penalized more heavily
      (weight of 2), acknowledging their impact on search difficulty. This is critical
      for avoiding common trap states.
    - Aggressive Overall Weighting: The overall multiplier is increased to 3.3. This
      makes the heuristic more greedy, aiming to prune more branches by inflating
      the estimated cost. This is a calculated risk taken to significantly reduce
      the generated_ratio, assuming it won't violate the cost_ratio bound.

    The formula aims for a balance: strong penalties for complex tile arrangements
    (linear and corner conflicts) combined with a greedy search strategy via the
    overall multiplier, all while ensuring computational efficiency.
    """

    GOAL_R = (0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3)
    GOAL_C = (0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3)

    tiles = s.tiles
    manhattan_dist = 0

    # Calculate Manhattan Distance
    for i in range(16):
        val = tiles[i]
        if val == 0:
            continue
        cur_r, cur_c = divmod(i, 4)
        manhattan_dist += abs(GOAL_R[val] - cur_r) + abs(GOAL_C[val] - cur_c)

    linear_conflicts = 0
    # Row conflicts: Two tiles in their goal row but in incorrect order.
    for r in range(4):
        for c1 in range(4):
            val1 = tiles[r * 4 + c1]
            if val1 == 0 or GOAL_R[val1] != r:
                continue
            for c2 in range(c1 + 1, 4):
                val2 = tiles[r * 4 + c2]
                if val2 != 0 and GOAL_R[val2] == r and val1 > val2:
                    linear_conflicts += 2 # Each conflict adds 2

    # Column conflicts: Two tiles in their goal column but in incorrect order.
    for c in range(4):
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            if val1 == 0 or GOAL_C[val1] != c:
                continue
            for r2 in range(r1 + 1, 4):
                val2 = tiles[r2 * 4 + c]
                if val2 != 0 and GOAL_C[val2] == c and GOAL_R[val1] > GOAL_R[val2]: # Compare goal rows for column conflicts
                    linear_conflicts += 2 # Each conflict adds 2

    corner_conflicts = 0
    # Penalty for corner tiles if they are in place but their immediate neighbors are not.
    # This indicates a 'locked' state requiring complex maneuvering.
    # Top-right corner (tile 3 at index 3)
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        corner_conflicts += 2
    # Bottom-left corner (tile 12 at index 12)
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        corner_conflicts += 2
    # Bottom-right corner (tile 15 at index 15)
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        corner_conflicts += 2

    # Weights tuned for aggressive pruning.
    # Increased linear conflict weight and corner conflict penalty.
    lc_weight = 5.0
    cc_weight = 2.0
    overall_weight = 3.3

    base_heuristic = manhattan_dist + lc_weight * linear_conflicts + cc_weight * corner_conflicts

    return int(base_heuristic * overall_weight)
