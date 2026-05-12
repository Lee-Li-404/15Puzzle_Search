from fifteen_state_class import State
import heapq
import itertools


'''
A* search implementation for the 15-puzzle.
This implementation uses a priority queue (min-heap) for the OPEN list,
and a set for the CLOSED list to track expanded states.
Reopening States: This implementation does NOT allow reopening of states in CLOSED.
Tie Breaking: FIFO tie-breaking is implemented by using a counter that increments with each insertion into the OPEN list.
Priority: it is determined first by f(s) = g(s) + h(s), then by the order of insertion (counter) to break ties.
Duplication Detection: Done by __eq__ function in fifteen_state_class.py
'''

def astar(start_state, heuristic):
    open_list = []
    counter = itertools.count()

    # g(s) = cost from start to s; f(s) = g(s) + h(s)
    g = {start_state: 0}
    f = {start_state: heuristic(start_state)}

    #Insert start node into OPEN with priority f(start)
    heapq.heappush(open_list, (f[start_state], next(counter), start_state))

    #Store nodes that have already been expanded
    closed = set()

    expanded = 0   # we never actually use this in h_search, but it's kept for consistency with previous code
    generated = 1  # start_state counts as generated
    seen = {start_state}  # track which states have ever been pushed to OPEN

    while open_list:
        _, _, current = heapq.heappop(open_list)
        expanded += 1

        if current.is_goal():
            return g[current], expanded, generated

        closed.add(current)

        for ns in current.neighbors():
            # no reopening: if the neighbor is already in CLOSED, skip it
            if ns in closed:
                continue

            ng = g[current] + 1

            # if the neighbor is not in OPEN (if not in g) or we found a cheaper path to it (ng < g[ns])
            if ns not in g or ng < g[ns]:
                g[ns] = ng
                f[ns] = ng + heuristic(ns)

                heapq.heappush(open_list, (f[ns], next(counter), ns))

                # count towards generated only when actually inserted into OPEN for the first time
                if ns not in seen:
                    seen.add(ns)
                    generated += 1

    print(f"[A*] Search ended — no solution found after {expanded} expansions, {generated} nodes generated")
    return float("inf"), expanded, generated



# ===== Basic Testing =====
from wa_md import make_heuristic
heuristic = make_heuristic(W=1.0)

def print_board(state):
    tiles = state.tiles
    for i in range(0, 16, 4):
        print(tiles[i:i+4])
    print()

if __name__ == "__main__":
    # ===== test cases =====
    tests = [
        # format: (tiles, expected optimal cost)

        # one move away
        ((1, 0, 2, 3,
          4, 5, 6, 7,
          8, 9,10,11,
          12,13,14,15), 1),

        # two moves away
        ((1, 2, 0, 3,
          4, 5, 6, 7,
          8, 9,10,11,
          12,13,14,15), 2),
        
        # already solved
        ((0, 1, 2, 3,
          4, 5, 6, 7,
          8, 9,10,11,
          12,13,14,15), 0),
    ]

    for i, (tiles, expected_cost) in enumerate(tests):
        start = State(tiles)

        print(f"=== Test {i+1} ===")
        print_board(start)

        cost, expanded, generated = astar(start, heuristic)

        print(f"Cost = {cost} (expected {expected_cost})")
        print(f"Expanded = {expanded}")
        print(f"Generated = {generated}")

        if cost != expected_cost:
            print("❌ WRONG COST")
        else:
            print("✅ OK")

        print("-" * 40)