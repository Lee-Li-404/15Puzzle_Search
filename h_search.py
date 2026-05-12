from google import genai
import os
from typing import List, Dict, Optional, Tuple
import sys
import datetime
from google.genai import errors as genai_errors
import asyncio
import multiprocessing as mp
from dotenv import load_dotenv
import os
import math
from program_selector import select_low_high_rand_from
from prompt_builder import build_best_shot_prompt
from model_generation import model_generate
from utils import safe_read_file, write_code, load_heuristic_from_file, BestEvalRecord, print_final_table
from island_handling import IslandState, print_summary, cull_and_refill, get_global_best_valid
from heuristic_evaluator import evaluate_file

# ============================================================
# User Configurable Parameters
# ============================================================

# Maximum allowed solution length/cost ratio during training.
# Example:
#   1.0 = strictly optimal
#   1.1 = up to 10% worse than optimal
COST_BOUND = 1.8

# Number of evolutionary search rounds.
# Each island generates one new heuristic per round.
TOTAL_ROUNDS = 23          # default: 23

# Perform island culling and global-best evaluation every N rounds.
# Set equal to TOTAL_ROUNDS to only evaluate at the end.
CHECKPOINT_INTERVAL = 8   # default: 8

# Number of parallel evolutionary islands (even numbers recommended for balanced culling).
# Each island maintains its own heuristic lineage.
NUM_ISLANDS = 8         # default: 8

# Print progress summaries every N rounds.
SUMMARY_INTERVAL = 1      # default: 1

# Random seed used for train/test dataset splitting.
TEST_TRAIN_SPLIT_SEED = 42



# ====== Optional Helper Params ======
ELITE_INJECT_COUNT = 2 # number of top elites to inject into culled islands at each checkpoint (default = 2)
MAX_CODE_CHARS = 200_000 # heuristic code length limit
EVAL_TIMEOUT_SEC = 1400 # seconds (set generously to allow for complex heuristics, but still enforce a hard limit)

# only evaluate on test_85 every X rounds to get score on test split for checking training progress, if this value 
# is large than TOTAL_ROUNDS, no evaluation on test set will be done during the search
TEST_EVAL_INTERVAL = 29 

API_MAX_CONCURRENCY = 8
CTX = mp.get_context("spawn") # use "spawn" to avoid issues with forking in PyPy and ensure clean process isolation during evaluation

# File name for fixed split created by sampler.py 
TRAIN_FULL_FILE = "train15.txt"   # used for search/selection
TEST_FULL_FILE  = "test85.txt"    # held-out evaluation

# ====== IO ======
FOLDER = "generated_programs"
os.makedirs(FOLDER, exist_ok=True)

# ====== Model call initialization ======
client = None
api_sem = None


#load Gemini API key from .env
load_dotenv() 
api_key_gemini = os.getenv("GEMINI_API_KEY")

if not api_key_gemini:
    print("[ERROR] GEMINI_API_KEY not found in environment variables.")
    sys.exit(1)

# Store best-over-time history for final reporting and plotting
BEST_HISTORY: List[BestEvalRecord] = []


# ====== Logger ======
class Logger(object):
    def __init__(self, logfile):
        self.terminal = sys.stdout
        self.log = open(logfile, "a", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()
        

# ====== Cleanup generated_programs Folder ======
def prepare_folder():
    os.makedirs(FOLDER, exist_ok=True)

    keep_files = {"generated_program_0.py", "generated_program_1.py"}

    for fname in os.listdir(FOLDER):
        path = os.path.join(FOLDER, fname)

        # only touch files, not subdirectories
        if os.path.isfile(path) and fname not in keep_files:
            try:
                os.remove(path)
            except Exception as e:
                print(f"[WARN] failed to delete {fname}: {e}")

# ===== Model generation ======
async def model_generate_async(prompt: str) -> str:
    global client
    async with api_sem:
        return await asyncio.to_thread(model_generate, prompt, client)


# ====== Bootstrap ======
def bootstrap_islands(num_islands: int = 8) -> List[IslandState]:
    """
    Initialize all islands with two starting admissible programs:
    - generated_program_0.py
    - generated_program_1.py
    """
    init_meta = [
        # (ver, score, path, generated_ratio, cost_ratio, is_valid) 
        # score and generated ratios here are placeholders only, not actual values
        (0, 1.0000, os.path.join(FOLDER, "generated_program_0.py"), 1.0, 1.0, True),
        (1, 1.0000, os.path.join(FOLDER, "generated_program_1.py"), 1.0, 1.0, True),
    ]

    states = []
    for i in range(num_islands):
        st = IslandState(island_id=i)
        for ver, score, path, generated, cost, valid in init_meta:
            code = safe_read_file(path)
            if not code:
                continue
            new_path = write_code(i, ver, code, FOLDER)
            st.results.append((ver, float(score), new_path, generated, cost, valid))
            print(
                f"[Bootstrap] island={i} v={ver} score={score:.4f} "
                f"gen={generated:.2f} cost={cost:.2f} valid={valid} -> {new_path}"
            )
        st.cnt = len(st.results)
        states.append(st)

    return states


# ===== Evaluation Wrapper for a Single Heuristic File ======
def eval_heuristic_on_filepath(heuristic_fn, filepath: str) -> Tuple[float, float]:
    """
    Wrapper to make intent explicit: returns (avg_generated_ratio, max_cost_ratio).
    """
    import evaluate_max as evaluate_max
    return evaluate_max.evaluate_astar(heuristic_fn, filepath)


# Returns the best heuristics discovered so far across all islands
def evaluate_best_fullsets(states: List[IslandState], round_idx: int) -> Optional[BestEvalRecord]:

    # Find the global best VALID heuristic across all islands so far (with cost ≤ COST_BOUND)
    gbest = get_global_best_valid(states)
    if gbest is None:
        return None

    island_id, rec = gbest
    ver, score, path, _, _, _ = rec[:6]
    heuristic = load_heuristic_from_file(path)

    # always evaluate training set 
    gen_train, cost_train = eval_heuristic_on_filepath(heuristic, TRAIN_FULL_FILE)

    # conditionally evaluate test every TEST_EVAL_INTERVAL rounds
    # usually skipped using a large TEST_EVAL_INTERVAL to save time
    if round_idx % TEST_EVAL_INTERVAL == 0:
        gen_test, cost_test = eval_heuristic_on_filepath(heuristic, TEST_FULL_FILE)
    else:
        gen_test, cost_test = float("nan"), float("nan")

    ts = datetime.datetime.now().isoformat(timespec="seconds")
    return BestEvalRecord(
        round_idx=round_idx,
        wall_time_iso=ts,
        island_id=island_id,
        version=int(ver),
        score=float(score),
        gen_train=float(gen_train),
        cost_train=float(cost_train),
        gen_test=float(gen_test),
        cost_test=float(cost_test),
    )


# ====== Main Iteration on a Single Island for a Single Round ======
async def generate_one_iteration_async(state: IslandState) -> Tuple[int, float]:
    try:
        # === 1️⃣ select best/worst + randoms heuristics on the island and add to prompt ===
        (low_code, low_score, low_meta), (high_code, high_score, high_meta), rand_list = \
            select_low_high_rand_from(state.results)

        #get recent two versions from the island so we can add them to the prompt
        prev_list = []
        for i in range(1, 3):  # last two iterations
            if len(state.results) >= i:
                _, prev_score, prev_path, _, _, _ = state.results[-i]
                prev_code = safe_read_file(prev_path)
                if prev_code:
                    prev_list.insert(0, (prev_code, prev_score))

        # === 2️⃣ build prompt ===
        prompt = build_best_shot_prompt(
            low_code=low_code,
            low_score=low_score,
            low_meta=low_meta,
            high_code=high_code,
            high_score=high_score,
            high_meta=high_meta,
            rand_list=rand_list,
            prev_list=prev_list,
            cost_bound=COST_BOUND,
        )

        # === 3️⃣ generate + evaluate ===
        new_code = await model_generate_async(prompt)
        path = write_code(state.island_id, state.cnt, new_code, FOLDER)

        # evaluate synchronously 
        generated_ratio, cost_ratio, score, is_valid = await asyncio.to_thread(evaluate_file, path, CTX, COST_BOUND, TEST_TRAIN_SPLIT_SEED,EVAL_TIMEOUT_SEC, TRAIN_FULL_FILE, TEST_FULL_FILE)

    #error handling: assign score of 999 if failed to generate or evaluate (but still record the attempt in the island history)
    except Exception as e:
        print(f"[WARN] island {state.island_id} v{state.cnt} gen failed: {e}")
        path = os.path.join(FOLDER, f"failed_{state.island_id}_{state.cnt}.py")
        with open(path, "w") as f:
            f.write("# failed\n")
        BAD_SCORE = 999.0
        generated_ratio, cost_ratio, score, is_valid = BAD_SCORE, BAD_SCORE, BAD_SCORE, False


    # === 4️⃣ record result ===
    state.results.append((state.cnt, score, path, generated_ratio, cost_ratio, is_valid))
    print(
        f"[Island {state.island_id} | v{state.cnt}] "
        f"gen={generated_ratio:.4f} cost={cost_ratio:.4f} valid={is_valid}"
    )
    state.cnt += 1
    return state.cnt - 1, score


# ====== Main Mutli-Island Generation and Evaluation ======
async def main_multi_islands():

    # Step 1: Bootstrap islands with initial heuristics
    states = bootstrap_islands(num_islands = NUM_ISLANDS)

    # Step 2: Main loop over rounds
    for r in range(TOTAL_ROUNDS):

        # For each island, generate a new heuristic in parallel and evaluate it
        tasks = [asyncio.create_task(generate_one_iteration_async(st)) for st in states]
        results_or_exc = await asyncio.gather(*tasks, return_exceptions=True)

        # Log any exceptions from the tasks
        for idx, res in enumerate(results_or_exc):
            if isinstance(res, Exception):
                print(f"[WARN] task failed on island {states[idx].island_id}: {res}")

        # Print summary every SUMMARY_INTERVAL rounds
        if (r + 1) % SUMMARY_INTERVAL == 0:
            print_summary(states, r)

        # Evaluate and report global best (across all islands) on full training set every round to track progress, and on test set every TEST_EVAL_INTERVAL rounds
        try:
            rec = await asyncio.to_thread(evaluate_best_fullsets, states, r + 1)
            if rec is None:
                print("[Summary] no valid heuristic under COST_BOUND yet")
            else:
                BEST_HISTORY.append(rec)

                if not math.isnan(rec.gen_test):
                    print(
                        f"[Summary] round={rec.round_idx} best=island {rec.island_id} v{rec.version} "
                        f"train(gen={rec.gen_train:.4f}, cost={rec.cost_train:.4f}) "
                        f"test(gen={rec.gen_test:.4f}, cost={rec.cost_test:.4f})"
                    )
                else:
                    print(
                        f"[Summary] round={rec.round_idx} best=island {rec.island_id} v{rec.version} "
                        f"train(gen={rec.gen_train:.4f}, cost={rec.cost_train:.4f}) "
                        f"test=SKIPPED"
                    )

        except Exception as e:
            print(f"[WARN] checkpoint eval failed: {e}")

        # Island Checkpoint: cull/refill islands and evaluate global best on training data every CHECKPOINT_INTERVAL rounds
        if (r + 1) % CHECKPOINT_INTERVAL == 0:
            cull_and_refill(states, ELITE_INJECT_COUNT=ELITE_INJECT_COUNT, FOLDER=FOLDER)
            print_summary(states, r)

    # print final summary of all islands at the end of the search process
    print("\n=== Final Results ===")
    for st in states:
        if st.results:
            best_valids = [r for r in st.results if len(r) >= 6 and r[5] is True]
            if best_valids:
                best = min(best_valids, key=lambda x: x[1])
                print(f"Island {st.island_id}: v{best[0]} score={best[1]:.4f} (valid, cost ≤ {COST_BOUND})")
            else:
                best = min(st.results, key=lambda x: x[1])
                print(
                    f"Island {st.island_id}: v{best[0]} score={best[1]:.4f} "
                    f"(NO VALID HEURISTIC, best cost={best[4]:.3f} > {COST_BOUND})"
                )

    # compute global best VALID heuristic
    all_results = [(st.island_id, *rec)
                for st in states
                for rec in st.results
                if rec]

    valid_results = [r for r in all_results if len(r) >= 7 and r[6] is True]

    if valid_results:
        gbest = min(valid_results, key=lambda x: x[2]) # minimize score
        print(
            f"\nGLOBAL BEST: island={gbest[0]} v={gbest[1]} "
            f"score={gbest[2]:.4f} | gen={gbest[4]:.3f} "
            f"cost={gbest[5]:.3f} | valid={gbest[6]}"
        )
    else:
        print("\nGLOBAL BEST: none (no valid heuristics under COST_BOUND)")


if __name__ == "__main__":

    #cleanup generated_programs folder but keep the two initial heuristics
    prepare_folder()

    #code for safe multiprocessing cleanup in PyPy (wont be used if using CPython, but no harm either)
    try:
        if mp.get_start_method(allow_none=True) != "spawn":
            mp.set_start_method("spawn", force=True)
    except RuntimeError:
        pass

    # Initialize global API client
    client = genai.Client(api_key=api_key_gemini)
    api_sem = asyncio.Semaphore(API_MAX_CONCURRENCY)

    # Logging setup
    log_dir = "logs"; os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    logfile = os.path.join(log_dir, f"log_{timestamp}.txt")
    sys.stdout = Logger(logfile)

    # ‼️ Main Step: Run the main async function for multi-island search
    asyncio.run(main_multi_islands())

    # GC and resource cleanup for PyPy 
    import gc, atexit
    @atexit.register
    def cleanup_resources():
        """Force garbage collection and release leaked semaphores (PyPy fix)."""
        import multiprocessing as mp
        try:
            # Touch active children to trigger cleanup of resource tracker
            mp.active_children()
        except Exception:
            pass
        gc.collect()
        print("[CLEANUP] Final GC cycle completed safely.")

    # Final reporting for best-over-time
    print_final_table(BEST_HISTORY)

