from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import ast
import textwrap
import os
import time
import importlib.util

'''
This file contains utility functions and data structures used across the project
'''


# Data class to keep track of the best heuristic evaluation record for checkpointing and final reporting
@dataclass
class BestEvalRecord:
    round_idx: int
    wall_time_iso: str
    island_id: int
    version: int
    score: float
    gen_train: float
    cost_train: float
    gen_test: float
    cost_test: float


# Utility functions for file reading 
def safe_read_file(path: str) -> Optional[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"[WARN] failed to read {path}: {e}")
        return None
    

# Extract heuristic code from model response text using multiple strategies
def try_extract_heuristic(code_text: Optional[str]) -> Optional[str]:
    if not code_text:
        return None
    try:
        tree = ast.parse(code_text)
    except SyntaxError as e:
        print(f"[WARN] unparsable code skipped: {e}")
        return None
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "heuristic":
            lines = code_text.splitlines()
            start = node.lineno - 1
            end = getattr(node, "end_lineno", len(lines))
            return textwrap.dedent("\n".join(lines[start:end]))
    print("[WARN] no def heuristic found")
    return None

# Write code to file and return the path
def write_code(island_id: int, cnt: int, code: str, folder: str) -> str:
    path = os.path.join(folder, f"generated_program_{island_id}_{cnt}.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    return path

# Load heuristic function from a given file path
def load_heuristic_from_file(path: str):
    unique_name = f"mod_{os.path.basename(path).replace('.py','')}_{int(time.time()*1e6)}"
    spec = importlib.util.spec_from_file_location(unique_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, "heuristic")


# Print a table of best records of each iteration after all rounds are done
def print_final_table(records: List[BestEvalRecord]):
    if not records:
        print("\n=== BEST CHECKPOINT HISTORY ===")
        print("No valid heuristic was found under COST_BOUND, so no checkpoints to report.")
        return

    headers = ["round", "island", "v", "score", "gen_train", "cost_train", "gen_test", "cost_test"]
    rows = []
    for r in records:
        rows.append([
            r.round_idx,
            r.island_id,
            r.version,
            f"{r.score:.6f}",
            f"{r.gen_train:.6f}",
            f"{r.cost_train:.6f}",
            f"{r.gen_test:.6f}",
            f"{r.cost_test:.6f}",
        ])

    # Pretty print without extra deps
    colw = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            colw[i] = max(colw[i], len(str(cell)))

    def fmt_row(row):
        return " | ".join(str(row[i]).rjust(colw[i]) for i in range(len(headers)))

    print("\n=== BEST CHECKPOINT HISTORY ===")
    print(fmt_row(headers))
    print("-+-".join("-" * w for w in colw))
    for row in rows:
        print(fmt_row(row))


# Note: not used currently for simplicity
def append_checkpoint_csv(records: List[BestEvalRecord], csv_path: str):
    # Writes full file each time to keep it simple and robust
    import csv
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "round",
            "time",
            "island",
            "version",
            "score",
            "gen_train",
            "cost_train",
            "gen_test",
            "cost_test",
        ])
        for r in records:
            w.writerow([
                r.round_idx,
                r.wall_time_iso,
                r.island_id,
                r.version,
                f"{r.score:.6f}",
                f"{r.gen_train:.6f}",
                f"{r.cost_train:.6f}",
                f"{r.gen_test:.6f}",
                f"{r.cost_test:.6f}",
            ])


