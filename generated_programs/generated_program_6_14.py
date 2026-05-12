from fifteen_state_class import State

def heuristic(s: State) -> int:
    """This heuristic evolves the previous best by incorporating an additional
    feature: the Manhattan distance of the blank tile from its goal position (0,0).
    The rationale is that states where the blank is closer to its home are generally
    preferable, as this facilitates solving the final block of tiles. This `blank_distance`
    term is added to the base heuristic (Manhattan Distance + Linear Conflicts)
    before the non-admissible weight is applied. This makes it a significant guiding
    component, intended to reduce search space by pruning paths that move the blank
    away from its goal without good reason.
    """
    WEIGHT = 2.5

    # GOAL_POS[val] -> (row, col)
    GOAL_POS = tuple((i // 4, i % 4) for i in range(16))

    manhattan_distance = 0
    blank_distance = 0
    
    # Calculate tile distances and find blank distance in one loop
    for i, val in enumerate(s.tiles):
        cur_r, cur_c = divmod(i, 4)
        if val == 0:
            blank_distance = cur_r + cur_c # MD of blank from (0,0)
            continue
        
        goal_r, goal_c = GOAL_POS[val]
        manhattan_distance += abs(goal_r - cur_r) + abs(goal_c - cur_c)

    # --- Linear Conflict Calculation ---
    linear_conflicts = 0
    tiles = s.tiles

    # Row conflicts: Count inversions for tiles in their goal row
    for r in range(4):
        goal_cols_in_row = []
        for c in range(4):
            val = tiles[r * 4 + c]
            if val != 0 and GOAL_POS[val][0] == r:
                goal_cols_in_row.append(GOAL_POS[val][1])
        
        n = len(goal_cols_in_row)
        for i in range(n):
            for j in range(i + 1, n):
                if goal_cols_in_row[i] > goal_cols_in_row[j]:
                    linear_conflicts += 1

    # Column conflicts: Count inversions for tiles in their goal column
    for c in range(4):
        goal_rows_in_col = []
        for r in range(4):
            val = tiles[r * 4 + c]
            if val != 0 and GOAL_POS[val][1] == c:
                goal_rows_in_col.append(GOAL_POS[val][0])
        
        n = len(goal_rows_in_col)
        for i in range(n):
            for j in range(i + 1, n):
                if goal_rows_in_col[i] > goal_rows_in_col[j]:
                    linear_conflicts += 1
                    
    # Combine components: MD, LC, and the new blank distance term.
    # Each linear conflict is standardly counted as adding 2 moves.
    base_h = manhattan_distance + (linear_conflicts * 2) + blank_distance
    
    return int(base_h * WEIGHT)