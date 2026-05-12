from typing import List, Dict, Optional, Tuple
import os
import random
from utils import safe_read_file

'''
Program selection logic for island evolution.
-given a list of evaluated heuristics with their scores and metadata, 
select the best (lowest score), worst (highest score), and a random heuristic
'''
def select_low_high_rand_from(results_list: List[Tuple[int, float, str, float, float, bool]]):
    # Expected record: (cnt, score, path, generated_ratio, cost_ratio, is_valid)

    # Keep only programs with actual file
    entries = [r for r in results_list if r[2] and os.path.exists(r[2])]
    if len(entries) < 2:
        raise RuntimeError("need at least two programs")

    # Split by validity
    valids   = [r for r in entries if r[5] is True]
    invalids = [r for r in entries if r[5] is False]

    # If no valids yet -> bootstrap: treat invalids as valids
    if not valids:
        valids = invalids.copy()

    # -------------------------------
    # HIGH and WORST must be VALID ONLY
    # -------------------------------
    sorted_valid = sorted(valids, key=lambda x: x[1])  # sort by score
    best  = sorted_valid[0]        # lowest score valid
    worst = sorted_valid[-1]       # highest score valid

    # -------------------------------
    # Random pool logic
    # -------------------------------
    # Key idea:
    # - If we have enough valid heuristics, use mostly valid random seeds
    # - If not, allow invalids to inject diversity
    # -------------------------------
    if len(valids) >= 4:
        # Mature phase → mostly use valid ones (except best/worst)
        rand_pool = sorted_valid[1:-1]  # middle valid heuristics
    else:
        # Early bootstrap → mix valid & invalid to explore
        rand_pool = valids + invalids

    # random pick up to 3 entries
    rand_choices = random.sample(rand_pool, min(3, len(rand_pool))) if rand_pool else []

    # Extract code + score for high/low/random
    low_code  = safe_read_file(worst[2])
    low_score = worst[1]
    low_meta  = {"generated_ratio": worst[3], "cost_ratio": worst[4]}

    high_code  = safe_read_file(best[2])
    high_score = best[1]
    high_meta  = {"generated_ratio": best[3], "cost_ratio": best[4]}

    rand_codes = [
        (safe_read_file(r[2]), r[1])
        for r in rand_choices
        if safe_read_file(r[2])
    ]

    return (low_code, low_score, low_meta), (high_code, high_score, high_meta), rand_codes
