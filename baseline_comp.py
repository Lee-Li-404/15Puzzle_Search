import time
import statistics
import matplotlib.pyplot as plt
import sampler 

from fifteen_state_class import State

# We will use the same A* implementation for both LLM and WA heuristics to ensure a fair comparison.
from astar_standard import astar

# ===== LLM heuristics =====
from heuristics_seed_42.generated_program_0_18 import heuristic as h17
from heuristics_seed_42.generated_program_0_22 import heuristic as h18
from heuristics_seed_42.generated_program_4_26 import heuristic as h19
from heuristics_seed_42.generated_program_1_22 import heuristic as h20
from heuristics_seed_42.generated_program_2_19 import heuristic as h21
from heuristics_seed_42.generated_program_4_23 import heuristic as h22
from heuristics_seed_42.generated_program_0_15 import heuristic as h23

# ===== WA heuristic factory =====
from wa_mdlc import make_heuristic


# ============================================================
# =============== SINGLE RUN (85 puzzles) ====================
# ============================================================
def evaluate_astar(heuristic, test_file):
    total_generated_ratio = []
    total_cost_ratio = []
    total_time = []

    with open(test_file) as f:
        lines = [line.strip() for line in f if line.strip()]

    for i in range(0, len(lines), 2):

        # Parse baseline data
        parts = lines[i].split()
        base_cost = float(parts[1])
        base_generated = float(parts[2])

        tiles = lines[i + 1].split()

        if len(tiles) == 17:
            tiles = tiles[1:]

        # Create state from tile configuration
        state = tuple(map(int, tiles))
        s = State(state)

        # Run A* with the given heuristic and measure time
        start = time.perf_counter()
        cost, expanded, generated = astar(s, heuristic)
        end = time.perf_counter()

        total_time.append(end - start)

        total_generated_ratio.append(generated / (base_generated + 1e-9))
        total_cost_ratio.append(cost / (base_cost + 1e-9))

    return (
        sum(total_generated_ratio) / len(total_generated_ratio),
        max(total_cost_ratio),
        sum(total_time) / len(total_time),
    )


# ============================================================
# ================= MULTI-RUN WRAPPER ========================
# ============================================================
def evaluate_with_repeats(heuristic, test_file, repeats=5):
    gen_list, cost_list, time_list = [], [], []

    for _ in range(repeats):
        g, c, t = evaluate_astar(heuristic, test_file)
        gen_list.append(g)
        cost_list.append(c)
        time_list.append(t)

    return {
        "gen_mean": statistics.mean(gen_list),
        "gen_std": statistics.stdev(gen_list) if repeats > 1 else 0,
        "cost_mean": statistics.mean(cost_list),
        "cost_max": max(cost_list),
        "time_mean": statistics.mean(time_list),
        "time_std": statistics.stdev(time_list) if repeats > 1 else 0,
    }


# ============================================================
# ======================== MAIN ==============================
# ============================================================
if __name__ == "__main__":


    # Test/Train split with seed 42 (the seed used for generating the LLM heuristics in heuristics_seed_42/)
    sampler.split_train_test(
            input_file="test_full.txt",
            train_file="train15_seed42.txt",
            test_file="test85_seed42.txt",
            train_size=15,
            seed=42,
        )

    # Use the seed 42 test set for evaluation for both LLM and WA heuristics to ensure a fair comparison.
    test_file = "test85_seed42.txt"

    # ===== LLM =====
    llm_heuristics = {
        "h17": h17,
        "h18": h18,
        "h19": h19,
        "h20": h20,
        "h21": h21,
        "h22": h22,
        "h23": h23,
    }

    # ===== WA =====
    # Generate WA heuristics with weights from 1.5 to 5.0 in increments of 0.1
    weight_list = [round(1.5 + 0.1 * k, 1) for k in range(int((5.0 - 1.5) / 0.1) + 1)]
    wa_heuristics = {f"W{w}": make_heuristic(w) for w in weight_list}

    all_results = {}

    # ===== Run LLM =====
    print("\n=== Running LLM heuristics ===")
    for name, h in llm_heuristics.items():
        print(f"\n{name}")
        all_results[name] = evaluate_with_repeats(h, test_file, 1)

    # ===== Run WA =====
    print("\n=== Running WA heuristics ===")
    for name, h in wa_heuristics.items():
        print(f"\n{name}")
        all_results[name] = evaluate_with_repeats(h, test_file, 1)

    # ======================================================
    # ================= PRINT TABLE =========================
    # ======================================================
    print("\n========== SUMMARY ==========")
    print(f"{'Name':<8}{'Gen(mean)':<12}{'Cost(max)':<12}{'Time(mean)':<12}")
    print("-" * 50)

    for k, v in all_results.items():
        print(f"{k:<8}{v['gen_mean']:<12.6f}{v['cost_max']:<12.6f}{v['time_mean']:<12.6f}")

    # ======================================================
    # ================= PLOT (COST vs TIME) ================
    # ======================================================
    wa_x, wa_y = [], []
    llm_x, llm_y = [], []

    for k, v in all_results.items():
        if k.startswith("W"):
            wa_x.append(v["cost_max"])
            wa_y.append(v["time_mean"])
        else:
            llm_x.append(v["cost_max"])
            llm_y.append(v["time_mean"])

    plt.figure(figsize=(8, 6))

    plt.scatter(wa_x, wa_y, label="WA*")
    plt.scatter(llm_x, llm_y, label="LLM")

    # annotate LLM
    for k, v in all_results.items():
        if not k.startswith("W"):
            plt.text(v["cost_max"], v["time_mean"], k)

    plt.xlabel("Cost Ratio (max observed)")
    plt.ylabel("Time (avg over runs)")
    plt.title("Cost vs Time")
    plt.legend()
    plt.grid(True, alpha=0.4)

    plt.show()

    # ===================================================================
    # ================= PLOT (COST vs GENERATED NODES RATIO) ============
    # ===================================================================
    wa_x2, wa_y2 = [], []
    llm_x2, llm_y2 = [], []

    for k, v in all_results.items():
        if k.startswith("W"):
            wa_x2.append(v["cost_max"])
            wa_y2.append(v["gen_mean"])
        else:
            llm_x2.append(v["cost_max"])
            llm_y2.append(v["gen_mean"])

    plt.figure(figsize=(8, 6))

    plt.scatter(wa_x2, wa_y2, label="WA*")
    plt.scatter(llm_x2, llm_y2, label="LLM")

    for k, v in all_results.items():
        if not k.startswith("W"):
            plt.text(v["cost_max"], v["gen_mean"], k)

    plt.xlabel("Cost Ratio (max observed)")
    plt.ylabel("Generated Ratio (avg)")
    plt.title("Cost vs Generated")
    plt.legend()
    plt.grid(True, alpha=0.4)

    plt.show()