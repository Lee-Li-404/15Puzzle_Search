import random
from typing import Optional, Tuple, List


def _read_pairs(input_file: str) -> List[Tuple[str, str]]:
    with open(input_file, "r") as f:
        lines = [line.rstrip("\n") for line in f]

    if len(lines) % 2 != 0:
        raise ValueError("Input file must contain an even number of lines")

    return [(lines[i], lines[i + 1]) for i in range(0, len(lines), 2)]


def _write_pairs(output_file: str, pairs: List[Tuple[str, str]]) -> None:
    with open(output_file, "w") as f:
        for line1, line2 in pairs:
            f.write(line1 + "\n")
            f.write(line2 + "\n")


def sample_15_puzzle_instances(
    input_file: str,
    output_file: str,
    num_samples: int = 15,
    seed: Optional[int] = None,
) -> None:
    """Randomly sample N instances (2 lines per instance) from input_file."""

    pairs = _read_pairs(input_file)

    if num_samples > len(pairs):
        raise ValueError(f"Requested {num_samples} samples, but only {len(pairs)} available")

    rng = random.Random(seed)
    sampled = rng.sample(pairs, num_samples)
    _write_pairs(output_file, sampled)


def split_train_test(
    input_file: str,
    train_file: str,
    test_file: str,
    train_size: int = 15,
    seed: Optional[int] = None,
) -> None:
    """
    Split instances into a fixed train set and a fixed test set using randomness + seed.

    - train_size instances go to train_file
    - the remaining instances go to test_file

    Deterministic if seed is provided.
    """

    pairs = _read_pairs(input_file)

    if train_size < 0 or train_size > len(pairs):
        raise ValueError(f"train_size must be in [0, {len(pairs)}]")

    rng = random.Random(seed)
    idxs = list(range(len(pairs)))
    rng.shuffle(idxs)

    train_pairs = [pairs[i] for i in idxs[:train_size]]
    test_pairs = [pairs[i] for i in idxs[train_size:]]

    _write_pairs(train_file, train_pairs)
    _write_pairs(test_file, test_pairs)


# === Example usage ===
if __name__ == "__main__":
    split_train_test(
        input_file="test_full.txt",
        train_file="train15.txt",
        test_file="test85.txt",
        train_size=15,
        seed=42,
    )
