from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic uses a Weighted A* approach on top of a strong admissible
    base heuristic: Manhattan Distance plus Linear Conflicts.

    1. Base Heuristic (h_base): This is the sum of Manhattan distances for all
       tiles and a penalty for linear conflicts. A linear conflict occurs when
       two tiles are in their correct row/column but are inverted relative to
       their goal positions. Each conflict adds at least two moves to the
       optimal solution, so we add 2 to the heuristic for each conflict pair.
       This h_base is admissible.

    2. Weighting (W): The base heuristic is multiplied by a weight W > 1.
       This makes the search greedier (favoring nodes with lower h-values more
       strongly), which significantly reduces the number of generated nodes.
       The trade-off is that the solution found is no longer guaranteed to be
       optimal. However, the path cost is bounded by W times the optimal cost.

    The cost_ratio limit is 1.80, so a weight up to 1.80 is theoretically
    safe. A weight of 1.5 is chosen as a robust value that should aggressively
    reduce node count while staying well within the cost limit.
    """
    GRID_SIZE = 4
    WEIGHT = 1.5  # Increased weight for greedier search

    # Precompute goal positions for O(1) lookup.
    GOAL_COORDS = tuple(divmod(val, GRID_SIZE) for val in range(GRID_SIZE * GRID_SIZE))

    md = 0
    lc = 0

    # Manhattan Distance Calculation
    for i, val in enumerate(s.tiles):
        if val == 0:
            continue
        cur_r, cur_c = divmod(i, GRID_SIZE)
        goal_r, goal_c = GOAL_COORDS[val]
        md += abs(goal_r - cur_r) + abs(goal_c - cur_c)

    # Linear Conflicts Calculation
    # Row conflicts
    for r in range(GRID_SIZE):
        tiles_in_goal_row = []
        for c in range(GRID_SIZE):
            val = s.tiles[r * GRID_SIZE + c]
            if val != 0 and GOAL_COORDS[val][0] == r:
                tiles_in_goal_row.append(val)

        # Sort tiles by their current column within this row to easily check inversions
        tiles_in_goal_row.sort(key=lambda v: divmod(s.tiles.index(v), GRID_SIZE)[1] if v in s.tiles else float('inf'))

        for i in range(len(tiles_in_goal_row)):
            for j in range(i + 1, len(tiles_in_goal_row)):
                val1 = tiles_in_goal_row[i]
                val2 = tiles_in_goal_row[j]
                goal_c1 = GOAL_COORDS[val1][1]
                goal_c2 = GOAL_COORDS[val2][1]

                # If tiles are in the same goal row and in correct order in current positions,
                # but their goal columns are inverted relative to each other.
                if goal_c1 > goal_c2:
                    lc += 1

    # Column conflicts
    for c in range(GRID_SIZE):
        tiles_in_goal_col = []
        for r in range(GRID_SIZE):
            val = s.tiles[r * GRID_SIZE + c]
            if val != 0 and GOAL_COORDS[val][1] == c:
                tiles_in_goal_col.append(val)

        # Sort tiles by their current row within this column to easily check inversions
        tiles_in_goal_col.sort(key=lambda v: divmod(s.tiles.index(v), GRID_SIZE)[0] if v in s.tiles else float('inf'))

        for i in range(len(tiles_in_goal_col)):
            for j in range(i + 1, len(tiles_in_goal_col)):
                val1 = tiles_in_goal_col[i]
                val2 = tiles_in_goal_col[j]
                goal_r1 = GOAL_COORDS[val1][0]
                goal_r2 = GOAL_COORDS[val2][0]

                # If tiles are in the same goal column and in correct order in current positions,
                # but their goal rows are inverted relative to each other.
                if goal_r1 > goal_r2:
                    lc += 1

    h_base = md + 2 * lc

    # Apply weight to make the heuristic greedier.
    # This helps reduce the number of generated nodes at the cost of potentially
    # a slightly longer solution path (bounded by WEIGHT).
    return int(h_base * WEIGHT)
