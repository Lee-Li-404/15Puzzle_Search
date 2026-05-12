from typing import Tuple, List

'''
Puzzle Goal State Representation from Korf's paper (Depth-First Iterative-Deepening: An Optimal Admissible Tree Search*):
0   1   2   3
4   5   6   7
8   9   10  11
12  13  14  15

0 represents the blank position, and the rest represent the numbered tiles.
'''

GOAL_TILES = tuple(range(16))  

class State:
    def __init__(self, tiles: Tuple[int, ...]):
        self.tiles = tiles
        self.blank_pos = tiles.index(0)

    #Check if the current state is the goal state
    def is_goal(self) -> bool:
        return self.tiles == GOAL_TILES

    #Generate neighboring states by sliding tiles into the blank position
    def neighbors(self) -> List["State"]:
        r, c = divmod(self.blank_pos, 4)
        result = []
        if r > 0:
            result.append(self._swap(self.blank_pos, self.blank_pos - 4))
        if r < 3:
            result.append(self._swap(self.blank_pos, self.blank_pos + 4))
        if c > 0:
            result.append(self._swap(self.blank_pos, self.blank_pos - 1))
        if c < 3:
            result.append(self._swap(self.blank_pos, self.blank_pos + 1))
        return result

    # Helper method to create a new state by swapping the blank with another tile
    def _swap(self, i: int, j: int) -> "State":
        new_tiles = list(self.tiles)
        new_tiles[i], new_tiles[j] = new_tiles[j], new_tiles[i]
        return State(tuple(new_tiles))

    # Implement hashing and equality to allow using State instances in sets and as dict keys
    def __hash__(self):
        return hash(self.tiles)

    # Equality comparison is based on the tile configuration
    def __eq__(self, other):
        return isinstance(other, State) and self.tiles == other.tiles
    


#===== Basic tests for State class =====
if __name__ == "__main__":
    print("Testing Equality...")
    state1 = State((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15))
    state2 = State((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15))
    state3 = State((1, 0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15))

    # If these fail, the script will throw an AssertionError and stop
    assert state1 == state2, "state1 should equal state2"
    assert state1 != state3, "state1 should not equal state3"
    print("Equality test passed")


    print("\nTesting Neighbors (Top-Left Corner)...")
    # 0 is in the top left, it can only swap with 1 (right) or 4 (down)
    initial_state = State((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15))
    neighbors = initial_state.neighbors()

    assert len(neighbors) == 2, f"Expected 2 neighbors, got {len(neighbors)}"

    expected_right = State((1, 0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15))
    expected_down = State((4, 1, 2, 3, 0, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15))

    assert expected_right in neighbors, "Failed to generate 'swap right' neighbor"
    assert expected_down in neighbors, "Failed to generate 'swap down' neighbor"
    print("Neighbors test Corner passed!")

    state5 = State((6, 1, 2, 3, 4, 5, 0, 7, 8, 9, 10, 11, 12, 13, 14, 15))
    print("\nTesting Neighbors (Middle Position)...")
    neighbors = state5.neighbors()
    expected_neighbors = [
        State((6, 1, 0, 3, 4, 5, 2, 7, 8, 9, 10, 11, 12, 13, 14, 15)),  
        State((6, 1, 2, 3, 4, 5, 10, 7, 8, 9, 0, 11, 12, 13, 14, 15)),  
        State((6, 1, 2, 3, 4, 0, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15)),  
        State((6, 1, 2, 3, 4, 5, 7, 0, 8, 9, 10, 11, 12, 13, 14, 15)),  
    ]
    for expected in expected_neighbors:
        assert expected in neighbors, f"Failed to generate expected neighbor: {expected.tiles}"
    print("Neighbors test passed for middle position!")