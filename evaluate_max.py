from fifteen_state_class import State
from astar_standard import astar

# example heuristic for testing
from heuristics_seed_42.generated_program_2_19 import heuristic as example_heuristic

def evaluate_astar(heuristic, test_file):
    """
    Evaluate heuristic using precomputed baseline (cost, generated)
    from test_file with format:
        id baseline_cost baseline_generated
        <16 tile numbers>
        ...
    Returns:
        generated_ratio (average)
        cost_ratio (maximum among all tests)
    """
    total_generated_ratio = []
    total_cost_ratio = []
    skipped = 0

    # Read test cases from file
    with open(test_file) as f:
        lines = [line.strip() for line in f if line.strip()]

    # Process each test case (2 lines per case)
    for i in range(0, len(lines), 2):
        try:
            parts = lines[i].split()

            # Basic validation of format
            if len(parts) < 3:
                print(f"[WARN] malformed baseline line: {lines[i]}")
                skipped += 1
                continue

            # keep optimal solution cost + baseline's # of generated nodes
            base_cost = float(parts[1])
            base_generated = float(parts[2])

            # Parse puzzle state line
            tiles = lines[i + 1].split()
            if len(tiles) == 17:
                tiles = tiles[1:]
            if len(tiles) != 16:
                print(f"[WARN] malformed state line: {lines[i+1]}")
                skipped += 1
                continue

            # state stores the tile configuration of the 15 puzzle
            state = tuple(map(int, tiles))

        # Handle any unexpected parsing errors gracefully
        except Exception as e:
            print(f"[WARN] skipped malformed pair at line {i+1}: {e}")
            skipped += 1
            continue

        s = State(state)

        # Run A* search and measure cost and generated nodes
        cost, expanded, generated = astar(s, heuristic)

        # Compute ratios
        # cost_ratio = our_cost / baseline_cost (lower is better)
        # generated_ratio = our_generated / baseline_generated (lower is better)
        cost_ratio = cost / (base_cost + 1e-9)
        generated_ratio = generated / (base_generated + 1e-9)

        print(f"[CASE {i//2 + 1}] cost={cost}, generated={generated}, "
              f"baseline_cost={base_cost}, baseline_generated={base_generated}")
        print(f"          → cost_ratio={cost_ratio:.4f}, generated_ratio={generated_ratio:.4f}")

        total_generated_ratio.append(generated_ratio)
        total_cost_ratio.append(cost_ratio)

    # Handle case where all tests were skipped (e.g., due to malformed input)
    if not total_generated_ratio:
        print(f"[WARN] no valid test cases, skipped={skipped}")
        return float("inf"), float("inf")

    # Use arithmetic average for generated ratio (to represent efficiency)
    avg_generated_ratio = sum(total_generated_ratio) / len(total_generated_ratio)
    
    # max_cost_ratio represents the OBSERVED worst-case cost performance across all test cases
    max_cost_ratio = max(total_cost_ratio)

    print(f"[EVAL] finished {len(total_generated_ratio)} puzzles (skipped={skipped})")
    print(f"[EVAL] avg_generated_ratio={avg_generated_ratio:.7f}, max_cost_ratio={max_cost_ratio:.7f}")

    return avg_generated_ratio, max_cost_ratio


# ===== Basic testing of evaluation function =====
if __name__ == "__main__":
    evaluate_astar(example_heuristic, "train15.txt")
