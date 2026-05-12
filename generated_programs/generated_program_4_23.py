from fifteen_state_class import State

def heuristic(s: State) -> int:
    """
    This heuristic aims to minimize generated nodes by increasing the penalty
    for linear conflicts and applying a more aggressive greedy multiplier.
    It builds on the successful combination of Manhattan Distance (MD), Linear
    Conflicts (LC), and Corner Conflicts (CC).

    Key changes:
    1. Increased Linear Conflict Weight: The penalty for linear conflicts is
       boosted to `lc * 12`. This provides a stronger deterrent against states
       with tiles in their correct row/column but in the wrong order, which
       are known to be problematic and increase search depth.

    2. Maintained Greedy Multiplier: The final multiplier is kept at 3.6.
       This value has proven effective in balancing search pruning and solution
       quality in recent iterations. The primary focus here is on the LC weight.

    The combination of a highly penalized LC term and a robust greedy multiplier
    is designed to significantly reduce the `generated_ratio` while ensuring the
    `cost_ratio` remains within the acceptable limit (<= 1.80).
    """
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

    md = 0  # Manhattan Distance
    for i, val in enumerate(tiles):
        if val != 0:
            md += MD_TABLE[i][val]

    lc = 0  # Linear Conflicts
    # Row conflicts
    for r in range(4):
        for c1 in range(4):
            val1 = tiles[r * 4 + c1]
            if val1 == 0 or GOAL_R[val1] != r:
                continue
            for c2 in range(c1 + 1, 4):
                val2 = tiles[r * 4 + c2]
                if val2 != 0 and GOAL_R[val2] == r and val1 > val2:
                    lc += 2

    # Column conflicts
    for c in range(4):
        for r1 in range(4):
            val1 = tiles[r1 * 4 + c]
            if val1 == 0 or GOAL_C[val1] != c:
                continue
            for r2 in range(r1 + 1, 4):
                val2 = tiles[r2 * 4 + c]
                if val2 != 0 and GOAL_C[val2] == c and GOAL_R[val1] > GOAL_R[val2]:
                    lc += 2

    cc = 0  # Corner Conflicts
    # Check if corner tiles are in place but are blocking other tiles.
    # Top-right corner (tile 3 at index 3)
    if tiles[3] == 3 and (tiles[2] != 2 or tiles[7] != 7):
        cc += 2
    # Bottom-left corner (tile 12 at index 12)
    if tiles[12] == 12 and (tiles[8] != 8 or tiles[13] != 13):
        cc += 2
    # Bottom-right corner (tile 15 at index 15)
    if tiles[15] == 15 and (tiles[11] != 11 or tiles[14] != 14):
        cc += 2

    # Base heuristic with a significantly increased penalty for linear conflicts.
    # The weight is increased to 12, up from 11 in previous best attempts.
    base_h = md + lc * 12 + cc

    # The overall greedy multiplier is maintained at 3.6.
    return int(base_h * 3.6)
