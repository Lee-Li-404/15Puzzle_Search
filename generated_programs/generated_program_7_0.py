from fifteen_state_class import State

def heuristic(s: State) -> int:
    """Extremely naive heuristic: 0 if goal, else 1."""
    return 0 if s.is_goal() else 1