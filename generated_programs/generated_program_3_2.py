from fifteen_state_class import State

def heuristic(s: State) -> int:
    """Calculates a heuristic value for the 15 Puzzle state.

    This heuristic combines the Manhattan distance with a penalty for tiles
    that are in the wrong row or column but not necessarily in their final
    position (linear conflicts).
    """
    GRID_SIZE = 4
    
    # Precompute goal positions for O(1) lookup.
    # The goal is assumed to be 0 1 2 3 ... 15 in reading order.
    GOAL_POS = [0] * (GRID_SIZE * GRID_SIZE)
    for i in range(GRID_SIZE * GRID_SIZE):
        GOAL_POS[i] = i

    dist = 0
    
    # Manhattan distance calculation
    for i, val in enumerate(s.tiles):
        if val == 0:  # Skip the blank tile
            continue
        
        # Calculate current row and column
        cur_r, cur_c = divmod(i, GRID_SIZE)
        
        # Calculate goal row and column
        goal_r, goal_c = divmod(GOAL_POS[val], GRID_SIZE)
        
        # Add Manhattan distance for this tile
        dist += abs(goal_r - cur_r) + abs(goal_c - cur_c)

    # Additional penalty for linear conflicts (tiles in the same row/column
    # that are in their goal row/column but not in their goal position).
    # This helps to break ties and provide a more informed heuristic.
    for i in range(GRID_SIZE * GRID_SIZE):
        if s.tiles[i] == 0: continue
        
        cur_r, cur_c = divmod(i, GRID_SIZE)
        val = s.tiles[i]
        goal_r, goal_c = divmod(GOAL_POS[val], GRID_SIZE)

        # Check for row conflicts
        if cur_r == goal_r:
            for j in range(i + 1, GRID_SIZE * GRID_SIZE):
                if s.tiles[j] == 0: continue
                
                cur_r2, cur_c2 = divmod(j, GRID_SIZE)
                val2 = s.tiles[j]
                goal_r2, goal_c2 = divmod(GOAL_POS[val2], GRID_SIZE)

                # If both tiles are in their goal row and their goal columns are
                # in the wrong order relative to each other.
                if cur_r2 == goal_r and goal_c2 < goal_c and cur_c2 > cur_c:
                    dist += 2 # Penalty for linear conflict

        # Check for column conflicts
        if cur_c == goal_c:
            for j in range(i + 1, GRID_SIZE * GRID_SIZE):
                if s.tiles[j] == 0: continue
                
                cur_r2, cur_c2 = divmod(j, GRID_SIZE)
                val2 = s.tiles[j]
                goal_r2, goal_c2 = divmod(GOAL_POS[val2], GRID_SIZE)

                # If both tiles are in their goal column and their goal rows are
                # in the wrong order relative to each other.
                if cur_c2 == goal_c and goal_r2 < goal_r and cur_r2 > cur_r:
                    dist += 2 # Penalty for linear conflict

    return dist
