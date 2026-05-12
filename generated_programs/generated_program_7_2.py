from fifteen_state_class import State

def heuristic(s: State) -> int:
    # Pre-compute goal positions for faster lookup
    GOAL_POS = [
        (0, 0), (0, 1), (0, 2), (0, 3),
        (1, 0), (1, 1), (1, 2), (1, 3),
        (2, 0), (2, 1), (2, 2), (2, 3),
        (3, 0), (3, 1), (3, 2), (3, 3)
    ]

    dist = 0
    for i, val in enumerate(s.tiles):
        if val == 0:
            continue
        # Current row and column
        cur_r, cur_c = divmod(i, 4)
        # Goal row and column for the current tile value
        goal_r, goal_c = GOAL_POS[val]
        
        # Manhattan distance for this tile
        dist += abs(goal_r - cur_r) + abs(goal_c - cur_c)

    # We can potentially add a heuristic enhancement. For a 4x4 grid, 
    # the maximum Manhattan distance for a single tile is 3+3=6. 
    # The total Manhattan distance can be significant. 
    # Let's try to penalize tiles that are far from their goal in a structured way. 
    # For example, tiles in the corner are harder to move out.
    # However, to keep it simple and efficient (O(16)), let's stick to Manhattan
    # and consider if we can make it slightly greedier without violating cost ratio.
    
    # The Manhattan distance is admissible. To make it potentially non-admissible
    # and greedier to reduce node generation, we could multiply it by a factor
    # slightly greater than 1, or add a constant. However, the prompt allows 
    # non-admissibility and focuses on reducing generated nodes.
    
    # A common technique for improving A* with Manhattan distance is to consider 
    # linear conflicts. However, implementing linear conflicts adds complexity and 
    # might not be O(16) if not done carefully. For O(16) and efficiency, 
    # simple Manhattan is usually a good baseline.
    
    # Let's evaluate if simply using Manhattan distance is enough or if we need 
    # to make it greedier. The previous best scores suggest that the standard 
    # Manhattan distance is performing well, but there might be room for 
    # improvement by making it a bit more aggressive if the cost ratio allows.
    
    # Since the goal is to reduce *unique nodes generated*, a slightly *higher* 
    # heuristic value for states that are still far from the goal can prune 
    # more branches. This is where non-admissibility can help.
    
    # A simple way to make Manhattan distance greedier is to add a small penalty 
    # or to adjust the estimate. 
    
    # Let's consider the properties of the 15 puzzle. 
    # The blank tile's position affects how easily other tiles can move.
    # The parity of the permutation also matters, but that's usually checked once.
    
    # If the standard Manhattan distance is performing well, a slight increase
    # might be beneficial for node generation. 
    # Let's try adding a small, tile-specific penalty. For example, tiles on 
    # the edges or corners might be considered 'harder' to move.
    
    # However, the prompt asks to avoid unnecessary nested loops and be O(16).
    # The current Manhattan calculation is O(16).
    
    # Let's think about a simple, non-admissible boost that's still efficient.
    # What if we add a bonus for tiles that are 'out of place' in a way that's
    # not captured by Manhattan distance alone? 
    
    # Example: A tile that is in the correct row but wrong column, or vice-versa.
    # This is already captured by Manhattan.
    
    # Consider the blank tile. Its position influences subsequent moves.
    # But directly incorporating the blank tile's position into the heuristic
    # for other tiles can be tricky to do efficiently and effectively.
    
    # Let's stick to modifying the tile-based heuristic values.
    # What if we give a 'bonus' for tiles that are very far away?
    # E.g., if a tile is in the top-left corner but belongs in the bottom-right.
    
    # A simpler, non-admissible modification: 
    # If a tile is *not* in its goal position, add a small constant penalty to the total.
    # This makes the heuristic value higher for any non-goal state.
    # E.g., `dist = dist + 1` for every tile not in its goal position.
    # However, this is almost like the `0 if s.is_goal() else 1` heuristic.
    
    # Let's consider Manhattan distance again. 
    # We have `dist` which is the sum of Manhattan distances for all tiles.
    # What if we add a penalty for tiles that are in the 'wrong' quadrant or
    # section of the board relative to their goal position?
    
    # For a 4x4 grid, let's consider rows/columns as segments.
    # If a tile's current row is far from its goal row, that contributes to Manhattan.
    
    # Let's try a simple, non-admissible adjustment: double the Manhattan distance.
    # This is highly admissible (if goal distance is d, estimate is 2d, so f=g+2d > g+d if g is cost).
    # However, `f = g + h`, so `f` increases. It might prune more.
    
    # Let's consider a simple multiplier. `dist * 1.5` would be a float.
    # We need an integer.
    
    # If `dist` is the sum of Manhattan distances, and the maximum possible value for 
    # a single tile's Manhattan distance is 6 (e.g., from (0,0) to (3,3)), 
    # the total Manhattan distance can be up to 15 * 6 = 90.
    
    # Let's try a modification that adds a penalty for tiles that are 'far' from their goal.
    # We could create a lookup table for 'difficulty' based on tile value.
    # But that's getting complex.
    
    # Let's stick to the Manhattan distance, and consider how to make it greedier.
    # The prompt says `cost_ratio <= 1.80`. This means we can afford to be
    # somewhat non-admissible to reduce generated nodes.
    
    # What if we add a penalty for tiles that are 'out of order' in a row/column?
    # E.g., tile 5 is before tile 4 when they should be ordered.
    # This is related to inversions, but more complex to calculate efficiently.
    
    # A simpler approach that might be greedier: 
    # For each tile, calculate its Manhattan distance. If this distance is large,
    # add an extra penalty. For example, if distance > 2, add 1 more.
    
    # Let's try this: compute Manhattan distance. If the tile is not in its goal cell,
    # add a small 'bias'. 
    
    # Let's try to be more aggressive with Manhattan. Instead of just summing, 
    # let's consider how far *away* from the goal row/column it is.
    
    # A standard technique to boost Manhattan is to consider linear conflicts.
    # But that is O(N^2) or O(N log N) in general. For 4x4, it might be feasible.
    # However, we are aiming for O(16) which is O(N^2) for N=4.
    
    # Let's revisit the O(16) constraint. The Manhattan distance is O(16).
    # The goal is to reduce generated nodes. If the cost ratio is low, we can afford to be greedy.
    
    # Consider the blank tile again. Its position matters.
    # What if we add a term related to how 'trapped' a tile is?
    
    # Let's try a simple, yet effective non-admissible heuristic.
    # Multiply Manhattan distance by a factor > 1.
    # For example, `int(dist * 1.2)`.
    # Or, add a small constant for every tile that is not in its goal cell.
    
    # Let's try this: 
    # Calculate Manhattan distance `dist`.
    # For each tile not in its goal position, add a fixed penalty.
    # E.g., if `abs(goal_r - cur_r) + abs(goal_c - cur_c) > 0`, add 1.
    # This means `dist_modified = dist + num_misplaced_tiles`.
    # This is still O(16) and potentially greedier.
    
    # Let's refine the Manhattan distance calculation.
    # The `GOAL_POS` lookup is good.
    
    # Consider this: what if we add a bonus for tiles that are in the 'wrong quarter' of the board?
    # This is getting complicated. 
    
    # The simplest way to make Manhattan non-admissible and greedier is to:
    # 1. Add a constant to every non-goal state (like `h=1 if not goal`).
    # 2. Multiply the Manhattan distance by a factor > 1 (e.g., `h = int(md * 1.1)`).
    # 3. Add penalties for specific configurations (like linear conflicts, which is complex).
    
    # Let's try a combination. Calculate Manhattan distance.
    # Then, add a penalty if the tile is in a 'difficult' position relative to its goal.
    
    # Consider the tile `val` at current position `i`.
    # Its goal position is `(goal_r, goal_c)`. Current position is `(cur_r, cur_c)`. 
    # Manhattan distance `md = abs(goal_r - cur_r) + abs(goal_c - cur_c)`. 
    
    # Let's try adding an extra penalty if `md` is large, for example, if `md >= 3`.
    # This means tiles that are far away get a bigger boost.
    
    # `dist += abs(goal_r - cur_r) + abs(goal_c - cur_c)`
    # `if abs(goal_r - cur_r) + abs(goal_c - cur_c) >= 3: dist += 2 # Extra penalty for far tiles`
    # This seems reasonable and maintains O(16).
    
    # Let's try to implement this.
    # We need to calculate the Manhattan distance for each tile first.
    
    modified_dist = 0
    for i, val in enumerate(s.tiles):
        if val == 0:
            continue
        
        cur_r, cur_c = divmod(i, 4)
        goal_r, goal_c = GOAL_POS[val]
        
        manhattan = abs(goal_r - cur_r) + abs(goal_c - cur_c)
        modified_dist += manhattan
        
        # Add an extra penalty if the tile is far from its goal.
        # This makes the heuristic more aggressive.
        # The threshold and penalty value can be tuned.
        # A threshold of 3 seems reasonable for a 4x4 grid.
        # A penalty of 2 might be too much or too little, needs tuning.
        # Let's try a smaller penalty, e.g., 1.
        if manhattan >= 3: # If the tile is at least 3 moves away in Manhattan distance
            modified_dist += 1 # Add a small extra penalty
            
    # The problem statement encourages a greedier heuristic if cost_ratio is low.
    # The default Manhattan distance has cost_ratio=1.0 and generated_ratio=1.0,
    # suggesting it's optimal in terms of solution length but not necessarily node generation.
    
    # The added penalty for distant tiles (manhattan >= 3) is a way to make the heuristic
    # more aggressive without being wildly inadmissible.
    # It's still O(16).
    
    # Let's consider the maximum possible Manhattan distance for a tile is 6.
    # The total Manhattan distance can be up to ~90.
    # Adding 1 for each tile with manhattan >= 3 adds at most 15 (if all tiles are far).
    # This is a small boost. 
    
    # Alternative: Multiply the Manhattan distance by a small factor.
    # E.g., `int(dist * 1.1)`. But this requires careful tuning of the factor.
    
    # Let's refine the 'far tile' penalty. Perhaps it should be proportional to distance?
    # `modified_dist += manhattan // 2` for `manhattan >= 2`?
    
    # Let's try a simpler, more direct approach that is known to work well.
    # Add a penalty for every tile that is not in its goal row OR goal column.
    # This is a simplification of linear conflicts.
    
    # Let's try another modification: calculate Manhattan distance.
    # Then, add a penalty related to the number of tiles NOT in their correct positions.
    # `dist_modified = dist + (number of tiles != goal_pos)`
    # The number of tiles not in their correct positions is `16 - num_correct_positions`.
    # This is simple and makes the heuristic higher for states with more misplaced tiles.
    
    # Let's recalculate with this idea.
    dist = 0
    misplaced_count = 0
    for i, val in enumerate(s.tiles):
        if val == 0:
            continue
        
        cur_r, cur_c = divmod(i, 4)
        goal_r, goal_c = GOAL_POS[val]
        
        manhattan = abs(goal_r - cur_r) + abs(goal_c - cur_c)
        dist += manhattan
        
        if manhattan > 0: # If the tile is not in its goal position
            misplaced_count += 1
    
    # Add the number of misplaced tiles as an additional heuristic component.
    # This is a common technique to make heuristics greedier.
    # The idea is that having many tiles out of place is generally harder to fix.
    # `total_heuristic = ManhattanDistance + misplaced_count`
    return dist + misplaced_count
