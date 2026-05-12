# wa_md.py
from fifteen_state_class import State

def make_heuristic(W: float):
    """
    Weighted Manhattan Distance heuristic for the 15-puzzle.

        h(s) = W * MD(s)

    where MD(s) is the standard Manhattan Distance to the goal.

    Parameters
    ----------
    W : float
        Weight multiplier applied to the Manhattan Distance.

    Returns
    -------
    function
        A heuristic function h(s: State) -> float.
    """

    # Precompute goal positions for tiles 0..15
    # Tile 0 (blank) will be ignored in the sum.
    GOAL_POS = tuple((v // 4, v % 4) for v in range(16))

    def heuristic(s: State) -> int:
        tiles = s.tiles
        dist = 0

        # --- Manhattan Distance only ---
        for pos, val in enumerate(tiles):
            #skip over blank tile
            if val == 0:
                continue
            goal_r, goal_c = GOAL_POS[val]
            r, c = divmod(pos, 4)
            dist += abs(r - goal_r) + abs(c - goal_c)

        return dist * W

    return heuristic



# ===== Basic Testing =====
if __name__ == "__main__":
    print(tuple((v // 4, v % 4) for v in range(16)))

    def print_board(state):
        tiles = state.tiles
        for i in range(0, 16, 4):
            print(tiles[i:i+4])
        print()

    tests = [
        tuple(range(16)),  # goal
        (0, 2, 1, 3,
         4, 5, 6, 7,
         8, 9,10,11,
         12,13,14,15),

        (1, 0, 2, 3,
         4, 5, 6, 7,
         8, 9,10,11,
         12,13,14,15),

        (0,1,2,3,
         4,5,6,7,
         8,9,10,11,
         12,13,15,14),

         
        (1, 2, 3, 4,
         5, 8, 7, 6,
         9, 10, 11, 12,
         13, 14, 15, 0),
    ]

    x = make_heuristic(1.0)

    for i, tiles in enumerate(tests):
        s = State(tiles)
        print(f"Test {i+1}")
        print_board(s)
        print("h =", x(s))
        print("-" * 30)