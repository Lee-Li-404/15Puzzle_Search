from dataclasses import dataclass, field
from typing import List, Tuple
from utils import safe_read_file, write_code



# this dataclass keeps track of the state of each island, including its history of generated heuristics and their scores
@dataclass
class IslandState:
    island_id: int

    # Tuple -> (ver, score, path, generated_ratio, cost_ratio, is_valid) 
    # ver is the same as cnt but we keep it for record-keeping. 
    results: List[Tuple[int, float, str, float, float, bool]] = field(default_factory=list)

    # counter for how many heuristics have been generated on this island (used for naming new files)
    cnt: int = 0


# Helper functions for summarizing island states and culling/refilling
def island_summary_str(state: IslandState) -> str:
    import math
    try:
        if not state.results:
            return f"Island {state.island_id} | empty"

        # split all generated heuristics on the island by validity
        valids = [r for r in state.results if len(r) >= 6 and r[5] is True]
        invalids = [r for r in state.results if len(r) >= 6 and r[5] is False]

        # last score for delta display
        last = state.results[-1]
        last_score = last[1] if len(last) >= 2 and isinstance(last[1], (int, float)) else float("inf")

        # mean cost over finite costs
        finite_costs = [
            r[4] for r in state.results
            if len(r) >= 6 and isinstance(r[4], (int, float)) and math.isfinite(r[4])
        ]
        mean_cost = (sum(finite_costs) / len(finite_costs)) if finite_costs else float("inf")

        valid_count = len(valids)
        invalid_count = len(invalids)
        valid_rate = valid_count / len(state.results) if state.results else 0.0

        # among valid heuristics, find the one with the best (lowest) score
        if valids:
            best = min(valids, key=lambda x: x[1])  # minimize score among valid only
            best_score, best_generated, best_cost = best[1], best[3], best[4]
            delta = last_score - best_score
            return (
                f"Island {state.island_id} | best={best_score:.4f} "
                f"(gen={best_generated:.4f}, cost={best_cost:.4f}) "
                f"| last={last_score:.4f} | Δ={delta:+.4f} | n={len(state.results)} "
                f"| valid={valid_count} | invalid={invalid_count} | valid_rate={valid_rate:.2f} "
                f"| mean_cost={(mean_cost if math.isfinite(mean_cost) else float('inf')) if isinstance(mean_cost, float) else mean_cost}"
            )
        else:
            # no feasible heuristics this island
            return (
                f"Island {state.island_id} | best=inf (no valid heuristics) "
                f"| last={last_score:.4f} | Δ=N/A | n={len(state.results)} "
                f"| valid=0 | invalid={invalid_count} | valid_rate=0.00 "
                f"| mean_cost={(mean_cost if math.isfinite(mean_cost) else float('inf')) if isinstance(mean_cost, float) else mean_cost}"
            )

    except Exception as e:
        return f"Island {state.island_id} | summary_error: {e}"
    

# Helper Function for printing summary of all islands in a round
def print_summary(states: List[IslandState], round_idx: int):
    print(f"\n===== ROUND {round_idx+1} SUMMARY =====")
    for st in states:
        print(island_summary_str(st))

    all_results = [
        (st.island_id, *rec)
        for st in states
        for rec in st.results if rec
    ]
    if not all_results:
        return

    # Only consider valid results for GLOBAL_BEST
    valid_results = [r for r in all_results if len(r) >= 7 and r[6] is True]

    if valid_results:
        gbest = min(valid_results, key=lambda x: x[2])  # x[2] = score
        print(
            f"GLOBAL_BEST: island={gbest[0]} v={gbest[1]} "
            f"score={gbest[2]:.4f} | gen={gbest[4]:.3f} cost={gbest[5]:.3f} | valid={gbest[6]}"
        )
    else:
        # Explicitly say “no valid heuristic under bound yet”
        print("GLOBAL_BEST: none (no valid heuristics under COST_BOUND yet)")

# ====== Cull & refill ======
def cull_and_refill(states: List[IslandState], ELITE_INJECT_COUNT: int = 2, FOLDER: str = "generated_programs"):
    """
    Cull the worst half of islands and inject a small number of elite
    heuristics from survivors. 
    """

    # -------------------------------------------------------
    # 1. Identify best individual from each island
    # -------------------------------------------------------
    island_bests = []
    for st in states:
        if st.results:
            valids = [r for r in st.results if r[5]]
            if valids:
                br = min(valids, key=lambda x: x[1])    # best valid
            else:
                br = min(st.results, key=lambda x: x[1]) # fallback
            island_bests.append((st, br))
        else:
            island_bests.append((st, (None, float("inf"), "", 1.0, 1.0, False)))

    # -------------------------------------------------------
    # 2. Rank islands by best score
    # -------------------------------------------------------
    ranked = sorted(island_bests, key=lambda x: x[1][1])  # sort by score
    survivors = [st for st, _ in ranked[:len(states)//2]]
    culled    = [st for st, _ in ranked[len(states)//2:]]

    print("\n=== CULL ===")
    print("Survivors:", [s.island_id for s in survivors])
    print("Culled:", [c.island_id for c in culled])

    # -------------------------------------------------------
    # 3. Collect top elites from survivors (valid-only preferred)
    # -------------------------------------------------------
    survivor_best_snippets = []
    for st in survivors:
        vr = [r for r in st.results if r[5]] or st.results
        br = min(vr, key=lambda x: x[1])
        cnt, score, path, gen_r, cost_r, valid = br[:6]
        survivor_best_snippets.append((score, safe_read_file(path), gen_r, cost_r, valid))

    # Sort survivor elites by best score
    survivor_best_snippets.sort(key=lambda x: x[0])  # lower score = better

    # -------------------------------------------------------
    # 4. Inject only top ELITE_INJECT_COUNT elites per culled island
    # -------------------------------------------------------
    for st in culled:
        print(f"[Inject] island {st.island_id}")

        st.results = [] # clear history 

        # Take the top few elites (default = 2)
        elites_to_inject = survivor_best_snippets[:ELITE_INJECT_COUNT]

        for (score, code_text, gen_r, cost_r, valid) in elites_to_inject:
            if not code_text:
                continue

            new_path = write_code(st.island_id, st.cnt, code_text, FOLDER)
            st.results.append((st.cnt, score, new_path, gen_r, cost_r, valid))
            print(f"   Injected elite with score={score:.4f}, cost={cost_r:.3f}, valid={valid}")
            st.cnt += 1


# Helper function to get global best valid heuristic across all islands (for migration and injection)
def get_global_best_valid(states: List[IslandState]):
    """
    Returns (island_id, rec) where rec is (cnt, score, path, generated_ratio, cost_ratio, is_valid).
    Only considers valid records. Returns None if no valid record exists yet.
    """
    all_valid = []
    for st in states:
        for rec in st.results:
            if not rec or len(rec) < 6:
                continue
            if rec[5] is True:
                all_valid.append((st.island_id, rec))

    if not all_valid:
        return None

    # rec[1] is score
    return min(all_valid, key=lambda x: x[1][1])