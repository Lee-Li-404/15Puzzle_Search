# wa_mdlc_new.py
from fifteen_state_class import State

def make_heuristic(W: float = 1.0):
    """
    Create a Weighted MD+LC heuristic:
        h(s) = W * (MD(s) + LC(s))

    Parameters
    ----------
    W : float
        Weight multiplier. MUST be 1.0 for the heuristic to remain admissible.
        Values > 1.0 turn this into Weighted A* (inadmissible, but faster).

    Returns
    -------
    function
        A heuristic function h(s) 
    """

    # Precompute goal positions once (closure scope)
    GOAL_POS = tuple((v // 4, v % 4) for v in range(16))

    def heuristic(s: State) -> float:
        tiles = s.tiles
        dist = 0

        # --- 1. Manhattan Distance ---
        for pos, val in enumerate(tiles):
            if val == 0:
                continue
            goal_r, goal_c = GOAL_POS[val]
            r, c = pos // 4, pos % 4
            dist += abs(r - goal_r) + abs(c - goal_c)

        # --- 2. Linear Conflict (Rows) ---
        for r in range(4):
            base = r * 4
            row_tiles = [tiles[base + i] for i in range(4)]
            
            # conflicts[i] will store a set of indices that tile i conflicts with
            conflicts = [set() for _ in range(4)]
            
            # Identify all conflicts in this row
            for i in range(4):
                v1 = row_tiles[i]
                if v1 == 0 or GOAL_POS[v1][0] != r:
                    continue  # Blank or doesn't belong in this row
                
                for j in range(i + 1, 4):
                    v2 = row_tiles[j]
                    if v2 == 0 or GOAL_POS[v2][0] != r:
                        continue
                    
                    # Both belong in this row. Are they out of order horizontally?
                    if GOAL_POS[v1][1] > GOAL_POS[v2][1]:
                        conflicts[i].add(j)
                        conflicts[j].add(i)
            
            # Resolve conflicts greedily
            while True:
                # Find the tile with the maximum number of conflicts
                max_conflicts = 0
                troublemaker_idx = -1
                
                for i in range(4):
                    c_len = len(conflicts[i])
                    if c_len > max_conflicts:
                        max_conflicts = c_len
                        troublemaker_idx = i
                
                # If no conflicts are left, we are done with this row
                if max_conflicts == 0:
                    break
                    
                # "Remove" the troublemaker: add 2 to distance (1 out, 1 in)
                dist += 2
                
                # Dynamically update the tiles it was conflicting with
                for conflicting_idx in conflicts[troublemaker_idx]:
                    conflicts[conflicting_idx].remove(troublemaker_idx)
                    
                # Clear the troublemaker's own conflicts
                conflicts[troublemaker_idx].clear()

        # --- 3. Linear Conflict (Columns) ---
        for c in range(4):
            col_tiles = [tiles[i * 4 + c] for i in range(4)]
            
            conflicts = [set() for _ in range(4)]
            
            # Identify all conflicts in this column
            for i in range(4):
                v1 = col_tiles[i]
                if v1 == 0 or GOAL_POS[v1][1] != c:
                    continue
                
                for j in range(i + 1, 4):
                    v2 = col_tiles[j]
                    if v2 == 0 or GOAL_POS[v2][1] != c:
                        continue
                    
                    # Both belong in this col. Are they out of order vertically?
                    if GOAL_POS[v1][0] > GOAL_POS[v2][0]:
                        conflicts[i].add(j)
                        conflicts[j].add(i)
            
            # Resolve conflicts greedily
            while True:
                max_conflicts = 0
                troublemaker_idx = -1
                
                for i in range(4):
                    c_len = len(conflicts[i])
                    if c_len > max_conflicts:
                        max_conflicts = c_len
                        troublemaker_idx = i
                
                if max_conflicts == 0:
                    break
                    
                dist += 2
                
                for conflicting_idx in conflicts[troublemaker_idx]:
                    conflicts[conflicting_idx].remove(troublemaker_idx)
                conflicts[troublemaker_idx].clear()

        return dist * W

    return heuristic


# ===== Basic Testing =====
if __name__ == "__main__":
    def print_board(state):
        tiles = state.tiles
        for i in range(0, 16, 4):
            print(tiles[i:i+4])
        print()

    # (tiles, description, expected h at W=1.0)
    tests = [
        (tuple(range(16)),
         "Goal state  (MD=0, LC=0)",
         0),

        ((0, 2, 1, 3,
          4, 5, 6, 7,
          8, 9,10,11,
         12,13,14,15),
         "Row 0: swap 1,2  (MD=2, LC=+2)",
         4),

        ((0, 5, 2, 3,
          4, 1, 6, 7,
          8, 9,10,11,
         12,13,14,15),
         "Col 1: swap 1,5  (MD=2, LC=+2)",
         4),

        ((0, 6, 2, 3,
          4, 5, 1, 7,
          8, 9,10,11,
         12,13,14,15),
         "Swap 1,6 across rows  (MD=4, LC=0  -- tiles leave their goal line)",
         4),

        ((3, 2, 1, 0,
          4, 5, 6, 7,
          8, 9,10,11,
         12,13,14,15),
         "Row 0 = [3,2,1,_]  (MD=5, LC=+4 from K3 conflict)",
         9),

        ((0, 1, 2, 3,
          8, 5, 6, 7,
          4, 9,10,11,
         12,13,14,15),
         "Col 0: swap 4,8  (MD=2, LC=+2)",
         4),

        ((1, 2, 3, 4,
          5, 8, 7, 6,
          9,10,11,12,
         13,14,15, 0),
         "Mixed state  (MD=22, LC=+2 from 7,6 in row 1)",
         24),
        
       ((0, 1, 2, 3,
          6, 13, 7, 4,
          8, 5,10,11,
         12, 9,14,15),
         "Mixed state (MD=10, LC=+4 in col 1)",
         14),
    ]

    print("=" * 55)
    print("Weighted MD+LC heuristic tests (W=1.0)")
    print("=" * 55)

    h = make_heuristic(1.0)
    passed = 0
    for i, (tiles, desc, expected) in enumerate(tests, 1):
        s = State(tiles)
        got = h(s)
        ok = got == expected
        passed += ok
        print(f"\nTest {i}: {desc}")
        print_board(s)
        print(f"  expected h = {expected}")
        print(f"  got      h = {got}")
        print(f"  {'PASS' if ok else 'FAIL'}")
        print("-" * 55)

    # Spot check the weight multiplier
    print("\nWeighted spot check  (W=2.5 on the row-swap case)")
    h2 = make_heuristic(2.5)
    s = State((0, 2, 1, 3,
               4, 5, 6, 7,
               8, 9,10,11,
              12,13,14,15))
    got = h2(s)
    expected = 4 * 2.5
    ok = abs(got - expected) < 1e-9
    passed += ok
    print(f"  expected h = {expected}")
    print(f"  got      h = {got}")
    print(f"  {'PASS' if ok else 'FAIL'}")

    total = len(tests) + 1
    print("\n" + "=" * 55)
    print(f"Summary: {passed}/{total} passed")
    print("=" * 55)