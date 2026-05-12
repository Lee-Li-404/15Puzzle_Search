from utils import load_heuristic_from_file
import multiprocessing as mp

TRAIN_FULL_FILE = "train15.txt"
TEST_FULL_FILE = "test85.txt"


'''
Evaluation Framework for Heuristic Functions in 15-Puzzle
1. test/train split (with fixed seed): 85(test)/15(train) split of test_full.txt into test85.txt and train15.txt
2. A* evaluation: for each heuristic, run A* on the 15 test cases in train15.txt, and compare against baseline cost and generated nodes from test85.txt
3. Returning two key metrics:
    - generated_ratio (average): (heuristic_generated / baseline_generated) averaged across all test
    - cost_ratio (max): maximum OBSERVED cost_ratio across all test 
'''

# test/train split and then evaluates a single heuristic file on the training set
def _eval_worker(path: str, out_q: mp.Queue, train_file: str, test_file: str, cost_bound, seed_no):
    try:
        import evaluate_max as evaluate_max
        import sampler as sampler

        # Load heuristic function from the given file path
        heuristic = load_heuristic_from_file(path)

        # Test / Train split with fixed seed 
        sampler.split_train_test(
            input_file="test_full.txt",
            train_file=train_file,
            test_file=test_file,
            train_size=15,
            seed=seed_no,
        )

        # Run evaluation and compute ratios
        generated_ratio, cost_ratio = evaluate_max.evaluate_astar(heuristic, train_file)

        # Determine validity based on cost ratio and cost bound, e.g. cost_bound = 1.2, cost_ratio = 1.3 -> is_valid = False
        is_valid = cost_ratio <= cost_bound

        #score = cost_ratio  (extra variable just for clarity)
        score = generated_ratio

        out_q.put((generated_ratio, cost_ratio, score, is_valid))
    except Exception as e:
        out_q.put(e)


def evaluate_file(path: str, CTX, cost_bound: float, seed_no: int, EVAL_TIMEOUT_SEC: int = 1600, train_file: str = TRAIN_FULL_FILE, test_file: str = TEST_FULL_FILE):
    """
    Evaluate a heuristic file safely.
    If evaluation fails (timeout/crash), return a finite penalty score
    Returns: (generated_ratio, cost_ratio, score, is_valid)
    """
    BAD_SCORE = 999.0  # finite fallback for evaluation failures

    out_q = CTX.Queue()
    proc = CTX.Process(target=_eval_worker, args=(path, out_q, train_file, test_file, cost_bound, seed_no))

    try:
        proc.start()
        proc.join(EVAL_TIMEOUT_SEC)

        # --- Handle Evaluation Timeout ---
        if proc.is_alive():
            proc.terminate()
            proc.join(1)
            print(f"[WARN] timeout evaluating {path}")
            return BAD_SCORE, BAD_SCORE, BAD_SCORE, False

        # --- Try to get result from queue ---
        try:
            result = out_q.get_nowait()
        except Exception as e:
            print(f"[WARN] eval infra error: {e}")
            return BAD_SCORE, BAD_SCORE, BAD_SCORE, False

        # --- Worker raised exception ---
        if isinstance(result, Exception):
            print(f"[WARN] eval failed: {result}")
            return BAD_SCORE, BAD_SCORE, BAD_SCORE, False

        # --- Normal result ---
        if isinstance(result, tuple) and len(result) == 4:
            generated_ratio, cost_ratio, score, is_valid = result
            status = "VALID" if is_valid else "HIGH_COST" # (invalid due to high cost (exceeding bound), but still returns a score for reference)
            print(f"[EVAL] generated={generated_ratio:.4f} cost={cost_ratio:.4f} -> {status}")
            return generated_ratio, cost_ratio, score, is_valid
    

        # --- Unexpected structure ---
        print(f"[EVAL] unexpected result: {result}")
        return BAD_SCORE, BAD_SCORE, BAD_SCORE, False

    except Exception as e:
        print(f"[FATAL] evaluate_file crashed: {e}")
        return BAD_SCORE, BAD_SCORE, BAD_SCORE, False

    finally:
        # ===== Safe cleanup =====
        import gc, time
        try:
            if proc.is_alive():
                proc.terminate()
        except Exception:
            pass

        try:
            proc.close()
        except Exception:
            pass

        try:
            out_q.close()
        except Exception:
            pass

        try:
            out_q.join_thread()
        except Exception:
            pass

        time.sleep(0.05)
        gc.collect()


