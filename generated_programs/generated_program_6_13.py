from fifteen_state_class import State

def heuristic(s: State) -> int:
    WEIGHT = 2.5

    goal_positions = tuple((i // 4, i % 4) for i in range(16))
    
    current_positions = [(0,0)] * 16
    for i, val in enumerate(s.tiles):
        current_positions[val] = (i // 4, i % 4)

    MANHATTAN_DISTANCE = 0
    LINEAR_CONFLICTS = 0
    
    max_individual_md = -1
    worst_tile_current_pos = (-1, -1)

    for val in range(1, 16):
        cur_r, cur_c = current_positions[val]
        goal_r, goal_c = goal_positions[val]
        
        md = abs(goal_r - cur_r) + abs(goal_c - cur_c)
        MANHATTAN_DISTANCE += md

        if md > max_individual_md:
            max_individual_md = md
            worst_tile_current_pos = (cur_r, cur_c)
            
    BLANK_TAX = 0
    if max_individual_md > 0:
        blank_r, blank_c = current_positions[0]
        worst_r, worst_c = worst_tile_current_pos
        BLANK_TAX = abs(blank_r - worst_r) + abs(blank_c - worst_c)

    for r in range(4):
        goal_cols_in_row = []
        for c in range(4):
            val = s.tiles[r * 4 + c]
            if val != 0 and goal_positions[val][0] == r:
                goal_cols_in_row.append(goal_positions[val][1])
        
        for i in range(len(goal_cols_in_row)):
            for j in range(i + 1, len(goal_cols_in_row)):
                if goal_cols_in_row[i] > goal_cols_in_row[j]:
                    LINEAR_CONFLICTS += 1
                    
    for c in range(4):
        goal_rows_in_col = []
        for r in range(4):
            val = s.tiles[r * 4 + c]
            if val != 0 and goal_positions[val][1] == c:
                goal_rows_in_col.append(goal_positions[val][0])
        
        for i in range(len(goal_rows_in_col)):
            for j in range(i + 1, len(goal_rows_in_col)):
                if goal_rows_in_col[i] > goal_rows_in_col[j]:
                    LINEAR_CONFLICTS += 1
    
    base_h = MANHATTAN_DISTANCE + (LINEAR_CONFLICTS * 2) + BLANK_TAX
    return int(base_h * WEIGHT)