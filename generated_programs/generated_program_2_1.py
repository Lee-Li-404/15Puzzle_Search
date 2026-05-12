from fifteen_state_class import State

def heuristic(s: State) -> int:
    """Naive Manhattan distance heuristic."""
    dist = 0
    for i, val in enumerate(s.tiles):
        if val == 0:
            continue
        goal_r, goal_c = divmod(val, 4)
        cur_r, cur_c = divmod(i, 4)
        dist += abs(goal_r - cur_r) + abs(goal_c - cur_c)
    return dist