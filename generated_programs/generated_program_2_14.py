from fifteen_state_class import State

def heuristic(s: State) -> int:
    GOAL_POS = (
        (0, 0), (0, 1), (0, 2), (0, 3),
        (1, 0), (1, 1), (1, 2), (1, 3),
        (2, 0), (2, 1), (2, 2), (2, 3),
        (3, 0), (3, 1), (3, 2), (3, 3)
    )

    tiles = s.tiles
    manhattan_dist = 0

    # Calculate Manhattan Distance
    for i in range(16):
        val = tiles[i]
        if val == 0:
            continue

        goal_r, goal_c = GOAL_POS[val]
        cur_r, cur_c = divmod(i, 4)
        manhattan_dist += abs(goal_r - cur_r) + abs(goal_c - cur_c)

    linear_conflicts = 0

    # Calculate Linear Conflicts
    # Check for row conflicts
    for r in range(4):
        current_row_tiles = []
        for c in range(4):
            val = tiles[r * 4 + c]
            if val != 0 and GOAL_POS[val][0] == r:
                current_row_tiles.append(val)

        for i in range(len(current_row_tiles)):
            val1 = current_row_tiles[i]
            for j in range(i + 1, len(current_row_tiles)):
                val2 = current_row_tiles[j]
                # If val1 appears before val2 (i < j) but its goal position
                # (represented by its value itself, since they are in their goal row)
                # is greater than val2's goal position in that row.
                if val1 > val2:
                    linear_conflicts += 1

    # Check for column conflicts
    for c in range(4):
        current_col_tiles = []
        for r in range(4):
            val = tiles[r * 4 + c]
            if val != 0 and GOAL_POS[val][1] == c:
                current_col_tiles.append(val)

        for i in range(len(current_col_tiles)):
            val1 = current_col_tiles[i]
            for j in range(i + 1, len(current_col_tiles)):
                val2 = current_col_tiles[j]
                # If val1 appears before val2 (i < j) but its goal position
                # (represented by its value itself, since they are in their goal column)
                # is greater than val2's goal position in that column.
                if val1 > val2:
                    linear_conflicts += 1

    # Previous best (score=0.0006, cost=1.776) used conflict_weight=3.5, overall_weight=3.2.
    # This resulted in an effective heuristic of 3.2*MD + 11.2*LC.
    # To further reduce generated nodes while carefully staying within the 1.80 cost_ratio bound,
    # we apply a very small increment to the overall_weight. This makes the heuristic slightly
    # greedier across both MD and LC components, aiming for a minimal impact on solution cost
    # while improving node generation efficiency.
    conflict_weight = 3.5
    overall_weight = 3.21  # Slightly increased from 3.2

    base_heuristic = manhattan_dist + conflict_weight * linear_conflicts

    return int(base_heuristic * overall_weight)