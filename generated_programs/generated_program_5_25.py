from fifteen_state_class import State

def heuristic(s: State) -> int:
    MD_TABLE = tuple(
        tuple(
            abs((i // 4) - (val // 4)) + abs((i % 4) - (val % 4))
            for val in range(16)
        )
        for i in range(16)
    )
    GOAL_R = tuple(val // 4 for val in range(16))
    GOAL_C = tuple(val % 4 for val in range(16))

    tiles = s.tiles
    manhattan_dist = 0
    
    for i, val in enumerate(tiles):
        if val != 0:
            manhattan_dist += MD_TABLE[i][val]

    linear_conflicts = 0

    # Row conflicts
    for r in range(4):
        for c1 in range(4):
            val1 = tiles[r * 4 + c1]
            if val1 == 0 or GOAL_R[val1] != r:
                continue
            for c2 in range(c1 + 1, 4):
                val2 = tiles[r * 4 + c2]
                if val2 != 0 and GOAL_R[val2] == r and val1 > val2:
                    linear_conflicts += 1
    
    # Column conflicts
    for c in range(4):
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            if val1 == 0 or GOAL_C[val1] != c:
                continue
            for r2 in range(r1 + 1, 4):
                val2 = tiles[r2 * 4 + c]
                if val2 != 0 and GOAL_C[val2] == c and val1 > val2:
                    linear_conflicts += 1

    # The previous best heuristic (score=0.0006, cost=1.776) used a conflict_weight of 3.6
    # and an overall_weight of 3.2. The cost_ratio is very close to the 1.80 limit.
    # This version makes a small, targeted increase to the linear conflict penalty, raising
    # it from 3.6 to 3.7. This makes the search more aggressively avoid states with these
    # hard-to-resolve patterns, aiming to reduce generated nodes. The overall weight is
    # maintained at 3.2 to avoid pushing the cost_ratio over the limit. This represents
    # a careful exploration at the edge of the solution quality boundary.
    conflict_weight = 3.7
    overall_weight = 3.2

    base_heuristic = manhattan_dist + conflict_weight * linear_conflicts

    return int(base_heuristic * overall_weight)