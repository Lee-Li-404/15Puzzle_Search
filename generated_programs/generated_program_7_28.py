from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic aims to further reduce generated nodes by refining the linear conflict calculation and slightly adjusting weights. It builds upon the successful components of previous versions, namely Manhattan Distance (MD) and Linear Conflicts (LC), while keeping the complexity low.

    Key changes:
    1.  Optimized Linear Conflict (LC) calculation: The LC calculation is made slightly more efficient by avoiding redundant checks. Each conflict is now weighted at 2, reflecting its impact on search difficulty.
    2.  Fine-tuned weights: The weights for MD and LC are adjusted to strike a better balance. The `lc_weight` is increased to 3.5 and the `overall_weight` is set to 3.2. This combination emphasizes penalizing linear conflicts more strongly, guiding the A* search towards more promising paths and reducing the number of generated nodes.

    The heuristic remains computationally efficient (O(N), where N=16) and aims to maintain a `cost_ratio` below 1.80 by leveraging the observed performance of similar weightings in previous iterations.
    """
    GOAL_R = (0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3)
    GOAL_C = (0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3)

    tiles = s.tiles
    manhattan_dist = 0

    # Calculate Manhattan Distance
    for i in range(16):
        val = tiles[i]
        if val == 0:  # Skip the blank tile
            continue
        cur_r, cur_c = divmod(i, 4)
        manhattan_dist += abs(GOAL_R[val] - cur_r) + abs(GOAL_C[val] - cur_c)

    linear_conflicts = 0
    # Row conflicts: Two tiles in their goal row but in incorrect order.
    for r in range(4):
        for c1 in range(4):
            val1 = tiles[r * 4 + c1]
            # Only consider tiles that belong in this row and are not blank
            if val1 == 0 or GOAL_R[val1] != r:
                continue
            for c2 in range(c1 + 1, 4):
                val2 = tiles[r * 4 + c2]
                # Only consider tiles that belong in this row and are not blank
                if val2 != 0 and GOAL_R[val2] == r and val1 > val2:
                    linear_conflicts += 2  # Each conflict adds 2

    # Column conflicts: Two tiles in their goal column but in incorrect order.
    for c in range(4):
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            # Only consider tiles that belong in this column and are not blank
            if val1 == 0 or GOAL_C[val1] != c:
                continue
            for r2 in range(r1 + 1, 4):
                val2 = tiles[r2 * 4 + c]
                # Only consider tiles that belong in this column and are not blank
                if val2 != 0 and GOAL_C[val2] == c and GOAL_R[val1] > GOAL_R[val2]:
                    linear_conflicts += 2  # Each conflict adds 2

    # Weights tuned for aggressive pruning.
    # Increased linear conflict weight to emphasize resolving order issues.
    lc_weight = 3.5
    # Overall weight to make the search more greedy.
    overall_weight = 3.2

    base_heuristic = manhattan_dist + lc_weight * linear_conflicts

    return int(base_heuristic * overall_weight)
