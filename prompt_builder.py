from typing import List, Dict, Optional, Tuple
import re
from utils import try_extract_heuristic

#rename function
def rename_func(def_text: str, new_name: str) -> str:
    return re.sub(r"def\s+heuristic\s*\(", f"def {new_name}(", def_text, count=1)

# ====== Prompt builder ======
def build_best_shot_prompt(
    low_code: str, low_score: float, low_meta: Dict[str, float],
    high_code: str, high_score: float, high_meta: Dict[str, float],
    rand_list: Optional[List[Tuple[str, float]]] = None,
    prev_list: Optional[List[Tuple[str, float]]] = None,
    cost_bound: float = 1.5
) -> str:
    """
    Build model prompt for evolving heuristics (15 Puzzle version)
    Includes generated_ratio, cost_ratio, and COST_BOUND.
    """
    low_def  = try_extract_heuristic(low_code)
    high_def = try_extract_heuristic(high_code)

    # fallback handling
    if high_def is None and low_def is not None:
        high_def, high_score, low_def, low_score = low_def, low_score, None, float("inf")
        high_meta = low_meta
    if high_def is None:
        high_def = (
            "def heuristic_v1(s: State):\n"
            "    # fallback placeholder\n"
            "    return 0\n"
        )
        high_score = float("inf")
        high_meta = {"generated_ratio": 1.0, "cost_ratio": 1.0}

    # Prompt Template
    header = (
        "You are an expert in combinatorial optimization and heuristic search algorithms.\n"
        "You are evolving a heuristic function for solving the 15 Puzzle (4×4 sliding tile puzzle) using A* search.\n"
        "\n"
        "Goal configuration:\n"
        " 0  1  2  3\n"
        " 4  5  6  7\n"
        " 8  9 10 11\n"
        "12 13 14 15\n"
        "Tile 0 is the blank tile located at the **top-left corner**.\n"
        "\n"
        "MUST start your code with:\n"
        "    from fifteen_state_class import State\n"
        "\n"
        "Reference:\n"
        "- State.tiles: tuple of 16 ints (0..15), where 0 is the blank.\n"
        "- State.neighbors() returns list of successor States.\n"
        "- State.is_goal() checks whether the puzzle is solved.\n"
        "\n"
        "Signature:\n"
        "def heuristic(s: State) -> int\n"
        "- Return a non-negative int estimate of remaining cost to goal.\n"
        "\n"
        "Rules:\n"
        "- The function does NOT need to be admissible.\n"
        "- Focus on reducing the total number of **unique nodes generated** during A* search.\n"
        f"- Keep cost_ratio ≤ {cost_bound:.2f}, where cost_ratio = solution_length / optimal_solution_length.\n"
        f"  This means the total solution cost (i.e., number of moves) must stay within COST_BOUND × optimal length.\n"
        "- The `cost_ratio` is the **WORST-CASE (MAXIMUM)** instance in the test set.\n"
        "- If your heuristic’s cost_ratio is well below the bound, it can safely become a bit greedier (larger estimates)\n"
        "  to further reduce generated nodes while still remaining valid.\n"
        "- Must be efficient: O(16) or better.\n"
        "- Avoid unnecessary nested loops.\n"
        "- Define all constants or lookup tables (like MANHATTAN_TABLE) **inside** the function.\n"
        "- Do NOT import, print, or reference any global variables or external files.\n"
        "\n"
        "Scoring metrics:\n"
        "- generated_ratio: lower is better (fewer unique nodes generated)\n"
        f"- cost_ratio: must be ≤ {cost_bound:.2f}\n"
        "\n"
        f"Current best: generated={high_meta['generated_ratio']:.3f}, cost={high_meta['cost_ratio']:.3f}, score={high_score:.4f}\n"
        f"Worse example: generated={low_meta['generated_ratio']:.3f}, cost={low_meta['cost_ratio']:.3f}, score={low_score:.4f}\n"
        "\n"
        "always return **valid Python code** implementing:\n"
        "    def heuristic(s: State) -> int\n"
        "\n"
        "⚠️ **VERY IMPORTANT — OUTPUT FORMAT REQUIREMENTS:** ⚠️\n"
        "- Output ONLY one JSON object.\n"
        "- The JSON must contain a single key named \"code\".\n"
        "- The value must be a string containing your full Python code.\n"
        "- Do NOT include explanations, markdown, or triple backticks.\n"
        "- Do NOT add text before or after the JSON.\n"
        "\n"
        "✅ **Example of correct output format:**\n"
        "{\n"
        "  \"code\": \"from fifteen_state_class import State\\n\\n"
        "def heuristic(s: State) -> int:\\n"
        "    dist = 0\\n"
        "    for i, val in enumerate(s.tiles):\\n"
        "        if val == 0: continue\\n"
        "        goal_r, goal_c = divmod(val, 4)\\n"
        "        cur_r, cur_c = divmod(i, 4)\\n"
        "        dist += abs(goal_r - cur_r) + abs(goal_c - cur_c)\\n"
        "    return dist\"\n"
        "}\n"
        "\n"
        "🧩 **Now output ONLY your improved heuristic in that JSON format.**"
    )

    

    prompt = header

    # === Previous round heuristics ===
    if prev_list:
        for i, (pc, ps) in enumerate(prev_list):
            if pc:
                prev_def = try_extract_heuristic(pc)
                if prev_def:
                    prompt += f"\n# === Previous (round -{len(prev_list)-i}) [score={ps:.4f}] ===\n"
                    prompt += rename_func(prev_def, f'heuristic_prev{i}') + "\n"

    # === Low (worse) and High (better) examples ===
    if low_def is not None:
        prompt += (
            f"\n# === Low (worse) heuristic_v0 [score={low_score:.4f}, "
            f"gen={low_meta['generated_ratio']:.3f}, cost={low_meta['cost_ratio']:.3f}] ===\n"
            + rename_func(low_def, 'heuristic_v0')
        )

    prompt += (
        f"\n\n# === High (better) heuristic_v1 [score={high_score:.4f}, "
        f"gen={high_meta['generated_ratio']:.3f}, cost={high_meta['cost_ratio']:.3f}] ===\n"
        + rename_func(high_def, 'heuristic_v1')
    )

    # === Random heuristics for exploration ===
    if rand_list:
        for idx, (rc, rs) in enumerate(rand_list):
            rdef = try_extract_heuristic(rc)
            if rdef:
                prompt += f"\n\n# === Random heuristic_vr{idx} [score={rs:.4f}] ===\n{rename_func(rdef, f'heuristic_vr{idx}')}"

    prompt += "\n\n# === Now produce improved final `heuristic` ===\n"
    return prompt