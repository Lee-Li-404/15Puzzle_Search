from fifteen_state_class import State
import heapq
import itertools


def astar(start_state: State, heuristic):
    """
    A* graph search for the 15-puzzle using the old unique generated-node
    convention.

    Generated nodes are states first inserted/discovered into OPEN. The start
    state counts once. Duplicate states, CLOSED states, stale heap entries, and
    improved paths to already discovered states are not counted again.
    """
    open_list = []
    counter = itertools.count()

    g = {start_state: 0}
    heapq.heappush(
        open_list,
        (heuristic(start_state), next(counter), start_state),
    )

    closed = set()
    expanded = 0
    generated = 1

    while open_list:
        _, _, current = heapq.heappop(open_list)

        if current in closed:
            continue

        expanded += 1

        if current.is_goal():
            return g[current], expanded, generated

        closed.add(current)

        for ns in current.neighbors():
            if ns in closed:
                continue

            ng = g[current] + 1

            if ns not in g:
                g[ns] = ng
                generated += 1
                heapq.heappush(
                    open_list,
                    (ng + heuristic(ns), next(counter), ns),
                )
            elif ng < g[ns]:
                g[ns] = ng
                heapq.heappush(
                    open_list,
                    (ng + heuristic(ns), next(counter), ns),
                )

    print(
        f"[A*] Search ended with no solution after "
        f"{expanded} expansions and {generated} generated nodes"
    )
    return float("inf"), expanded, generated
