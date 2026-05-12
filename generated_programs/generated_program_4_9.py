from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    Evolves the weighted Manhattan Distance (MD) + Linear Conflicts (LC) heuristic.
    The previous best heuristic (score=0.0029, gen=0.003, cost=1.219) used MD + 2*LC
    with a weight of 1.71. It had significant headroom on the cost_ratio (1.219 vs 1.80).
    Experiments showed that simply increasing the weight worsened performance, suggesting
    a more informed heuristic is needed.

    This version introduces a "lock penalty" to identify specific, known-difficult board
    configurations that are not fully captured by MD or LC. These occur when tiles are
    in their goal positions but trap other tiles or the blank space, making the puzzle
    harder to solve. By adding a small, targeted penalty for these states, the search
    can be guided away from these traps, hopefully reducing the number of generated nodes.

    The new components are:
    1.  Corner Lock Penalty: If a corner tile (e.g., 3, 12, 15) is in its goal spot,
        but its adjacent tiles are not, a penalty is added.
    2.  Blank Trap Penalty: A special, larger penalty is added if tiles 1 and 4 are
        in their goal positions, trapping the blank space away from its home corner.

    The overall weight of 1.71 is retained, as it proved effective. The new penalties
    selectively increase the heuristic's value to make it greedier in these critical situations.
    """
    # GOAL_RC[tile_value] -> (goal_row, goal_col). Pre-calculated for O(1) lookups.
    GOAL_RC = (
        (0, 0), (0, 1), (0, 2), (0, 3),
        (1, 0), (1, 1), (1, 2), (1, 3),
        (2, 0), (2, 1), (2, 2), (2, 3),
        (3, 0), (3, 1), (3, 2), (3, 3),
    )

    tiles = s.tiles
    manhattan_dist = 0

    # 1. Manhattan Distance Calculation
    for i in range(16):
        val = tiles[i]
        if val == 0:
            continue
        goal_r, goal_c = GOAL_RC[val]
        cur_r, cur_c = i // 4, i % 4
        manhattan_dist += abs(goal_r - cur_r) + abs(goal_c - cur_c)

    # 2. Linear Conflicts Calculation
    conflicts = 0
    # Row conflicts
    for r in range(4):
        for c1 in range(4):
            val1 = tiles[r * 4 + c1]
            if val1 == 0 or GOAL_RC[val1][0] != r:
                continue
            for c2 in range(c1 + 1, 4):
                val2 = tiles[r * 4 + c2]
                if val2 != 0 and GOAL_RC[val2][0] == r and val1 > val2:
                    conflicts += 1
    # Column conflicts
    for c in range(4):
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            if val1 == 0 or GOAL_RC[val1][1] != c:
                continue
            for r2 in range(r1 + 1, 4):
                val2 = tiles[r2 * 4 + c]
                if val2 != 0 and GOAL_RC[val2][1] == c and GOAL_RC[val1][0] > GOAL_RC[val2][0]:
                    conflicts += 1
    linear_conflicts_cost = conflicts * 2

    # 3. Lock Penalties for known difficult configurations
    lock_penalty = 0
    # A blank trap is a severe lock. If tiles 1 and 4 are in their goal positions,
    # it becomes very difficult to move the blank tile back to position 0.
    if tiles[0] != 0 and tiles[1] == 1 and tiles[4] == 4:
        lock_penalty += 4

    # Corner locks: Penalize if a corner tile is in place but its neighbors are not.
    # This configuration makes it hard to correctly place the neighbors.
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        lock_penalty += 2
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        lock_penalty += 2
    if tiles[15] == 15 and (tiles[14] != 14 or tiles[11] != 11):
        lock_penalty += 2

    # 4. Combine and Weight
    base_h = manhattan_dist + linear_conflicts_cost + lock_penalty

    # Use the same weight as the previous best version. The added lock penalties
    # provide a more informed way to increase greediness in specific trap states.
    WEIGHT = 1.71

    return int(base_h * WEIGHT)