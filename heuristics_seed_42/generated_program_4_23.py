from fifteen_state_class import State
#    23 |      4 | 23 | 0.001049 |  0.001049 |   1.285714 | 0.000551 |  1.346154  
#1.35
def heuristic(s: State) -> int:
    """An enhanced heuristic combining Manhattan distance, weighted linear conflicts,
    a generalized trap penalty, and specific endgame pattern recognition.
    """
    # 1. Memoization for precomputed tables. Using a function attribute for state.
    _memo = getattr(heuristic, '_memo', None)
    if _memo is None:
        MANHATTAN = tuple(
            tuple(abs(pos // 4 - val // 4) + abs(pos % 4 - val % 4) for val in range(16))
            for pos in range(16)
        )
        GOAL_R = tuple(v // 4 for v in range(16))
        GOAL_C = tuple(v % 4 for v in range(16))
        ADJ = tuple(
            tuple(sorted(n for n in (i-4, i+4, i-1, i+1) if 0 <= n < 16 and (abs(i//4 - n//4) + abs(i%4 - n%4) == 1)))
            for i in range(16)
        )
        _memo = (MANHATTAN, GOAL_R, GOAL_C, ADJ)
        setattr(heuristic, '_memo', _memo)

    MANHATTAN, GOAL_R, GOAL_C, ADJ = _memo
    tiles = s.tiles
    
    md = 0
    lc = 0
    penalties = 0

    # 2. Manhattan Distance
    for i in range(16):
        val = tiles[i]
        if val != 0:
            md += MANHATTAN[i][val]

    if md == 0: return 0

    # 3. Weighted Linear Conflicts (penalty=4)
    for r in range(4):
        row_conflicts = []
        for c in range(4):
            val = tiles[r * 4 + c]
            if val != 0 and GOAL_R[val] == r:
                row_conflicts.append(val)
        cnt = len(row_conflicts)
        if cnt > 1:
            for i in range(cnt):
                for j in range(i + 1, cnt):
                    if GOAL_C[row_conflicts[i]] > GOAL_C[row_conflicts[j]]:
                        lc += 4

    for c in range(4):
        col_conflicts = []
        for r in range(4):
            val = tiles[r * 4 + c]
            if val != 0 and GOAL_C[val] == c:
                col_conflicts.append(val)
        cnt = len(col_conflicts)
        if cnt > 1:
            for i in range(cnt):
                for j in range(i + 1, cnt):
                    if GOAL_R[col_conflicts[i]] > GOAL_R[col_conflicts[j]]:
                        lc += 4

    # 4. Penalties for difficult patterns
    # A. Generalized Trap Penalty: A misplaced tile locked by solved neighbors.
    for i in range(16):
        val = tiles[i]
        if val == 0 or val == i: continue
        
        is_trapped = True
        for neighbor_pos in ADJ[i]:
            neighbor_val = tiles[neighbor_pos]
            if neighbor_val == 0 or neighbor_val != neighbor_pos:
                is_trapped = False
                break
        if is_trapped:
            penalties += 4

    # B. Specific Endgame Deadlocks
    if tiles[11] == 11 and tiles[14] == 15 and tiles[15] == 14:
        penalties += 6
    if tiles[7] == 7 and tiles[11] == 15 and tiles[15] == 11:
        penalties += 6
        
    # C. Endgame Zone Penalty
    solved_count = 0
    for i in range(12):
        if tiles[i] == i:
            solved_count += 1
    if solved_count >= 10:
        # Penalize misplaced tiles in the last row when close to solving top rows.
        for i in range(12, 16):
            if tiles[i] != i and tiles[i] != 0:
                penalties += 5
    
    # 5. Final Aggregation and Weighting
    h_base = md + lc + penalties
    
    # Use the same successful weight (1.75) from the previous best heuristic.
    # The improved base heuristic (h_base) is already higher on average,
    # so this makes the overall heuristic greedier without risking the cost ratio.
    return (h_base * 7) // 4