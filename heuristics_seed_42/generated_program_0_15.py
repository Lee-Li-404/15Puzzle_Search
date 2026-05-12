from fifteen_state_class import State
#   23 |      0 | 15 | 0.000369 |  0.000369 |   1.560000 | 0.000302 |  1.705882
# 1.75
def heuristic(s: State) -> int:
    """
    A state-of-the-art heuristic evolving from the best previous attempts.
    It combines three distinct components, guided by different strategic insights,
    into a single, powerful non-admissible estimate.

    1.  Weighted MD+LC Core: A highly-tuned, non-admissible version of the
        classic Manhattan Distance plus Linear Conflicts heuristic. The core
        is aggressively weighted to prune the search space effectively, using
        an unrolled, O(1) implementation for maximum speed.

    2.  Last Mover Blank Penalty (LMBP): This intelligent component identifies
        the highest-valued tile that is out of place and adds a penalty equal
        to the distance from the blank tile to that tile's goal. This directs
        the search to solve the "hardest" parts of the puzzle first, mimicking
        expert human strategy.

    3.  Blank Isolation Penalty (BIP): A novel component that penalizes the
        blank tile for being surrounded by tiles that are already correctly
        placed. This discourages wasting moves shuffling correct tiles and
        pushes the blank towards the "action zone" of misplaced tiles, further
        improving search efficiency.

    The combination of these components provides a multi-faceted view of the
    puzzle's difficulty, leading to superior pruning and a significant reduction
    in generated nodes while staying within the required solution cost bounds.
    """
    tiles = s.tiles

    # --- Static Tables (defined once) ---
    if not hasattr(heuristic, "MANHATTAN_TABLE"):
        heuristic.MANHATTAN_TABLE = tuple(
            tuple(
                abs(pos // 4 - val // 4) + abs(pos % 4 - val % 4)
                for val in range(16)
            )
            for pos in range(16)
        )
        heuristic.NEIGHBORS = (
            (1, 4), (0, 2, 5), (1, 3, 6), (2, 7),
            (0, 5, 8), (1, 4, 6, 9), (2, 5, 7, 10), (3, 6, 11),
            (4, 9, 12), (5, 8, 10, 13), (6, 9, 11, 14), (7, 10, 15),
            (8, 13), (9, 12, 14), (10, 13, 15), (11, 14)
        )

    md = 0
    lc_pairs = 0
    blank_pos = -1
    t_md = heuristic.MANHATTAN_TABLE

    # --- 1. MD and Blank Position ---
    for i, val in enumerate(tiles):
        if val:
            md += t_md[i][val]
        else:
            blank_pos = i

    # --- 2. Linear Conflicts (unrolled) ---
    # Row Conflicts
    for r in range(4):
        base = r << 2
        t0 = tiles[base]
        if t0 and (t0 >> 2) == r:
            t1 = tiles[base + 1]
            if t1 and (t1 >> 2) == r and t0 > t1: lc_pairs += 1
            t2 = tiles[base + 2]
            if t2 and (t2 >> 2) == r and t0 > t2: lc_pairs += 1
            t3 = tiles[base + 3]
            if t3 and (t3 >> 2) == r and t0 > t3: lc_pairs += 1
        t1 = tiles[base + 1]
        if t1 and (t1 >> 2) == r:
            t2 = tiles[base + 2]
            if t2 and (t2 >> 2) == r and t1 > t2: lc_pairs += 1
            t3 = tiles[base + 3]
            if t3 and (t3 >> 2) == r and t1 > t3: lc_pairs += 1
        t2 = tiles[base + 2]
        if t2 and (t2 >> 2) == r:
            t3 = tiles[base + 3]
            if t3 and (t3 >> 2) == r and t2 > t3: lc_pairs += 1
    # Column Conflicts
    for c in range(4):
        t0 = tiles[c]
        if t0 and (t0 & 3) == c:
            t1 = tiles[c + 4]
            if t1 and (t1 & 3) == c and t0 > t1: lc_pairs += 1
            t2 = tiles[c + 8]
            if t2 and (t2 & 3) == c and t0 > t2: lc_pairs += 1
            t3 = tiles[c + 12]
            if t3 and (t3 & 3) == c and t0 > t3: lc_pairs += 1
        t1 = tiles[c + 4]
        if t1 and (t1 & 3) == c:
            t2 = tiles[c + 8]
            if t2 and (t2 & 3) == c and t1 > t2: lc_pairs += 1
            t3 = tiles[c + 12]
            if t3 and (t3 & 3) == c and t1 > t3: lc_pairs += 1
        t2 = tiles[c + 8]
        if t2 and (t2 & 3) == c:
            t3 = tiles[c + 12]
            if t3 and (t3 & 3) == c and t2 > t3: lc_pairs += 1

    # --- 3. Last Mover Blank Penalty (LMBP) ---
    lmbp = 0
    last_misplaced_goal_pos = 0
    # The goal position of tile `k` is index `k`.
    # We check if the tile at that goal position is correct.
    for k in range(15, 0, -1):
        if tiles[k] != k:
            last_misplaced_goal_pos = k
            break
    if last_misplaced_goal_pos > 0:
        # Penalty is MD between blank and the goal position of the last misplaced tile
        lmbp = t_md[blank_pos][last_misplaced_goal_pos]

    # --- 4. Blank Isolation Penalty (BIP) ---
    bip = 0
    # Penalty of 2 if a neighbor of the blank is already in its goal state.
    for neighbor_pos in heuristic.NEIGHBORS[blank_pos]:
        if tiles[neighbor_pos] == neighbor_pos:
            bip += 2
    
    # --- 5. Final Weighted Heuristic ---
    # The base weight (2.80 for MD, 5.60 for LC pairs) is tuned to be aggressive
    # yet leave room for the additional intelligent penalties (LMBP, BIP)
    # without exceeding the cost ratio limit.
    base_h = (280 * md + 560 * lc_pairs) // 100
    
    return base_h + lmbp + bip