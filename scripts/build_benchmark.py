#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from hien_soundmatch.benchmarking import BenchmarkConfig, save_benchmark


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the Hindi-English sound-matching benchmark.")
    parser.add_argument("--raw", type=Path, default=Path("data/raw/crowd_transliterations.hi-en.txt"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/benchmark.csv"))
    parser.add_argument("--test-fraction", type=float, default=0.25)
    parser.add_argument("--random-state", type=int, default=42)
    args = parser.parse_args()

    config = BenchmarkConfig(test_fraction=args.test_fraction, random_state=args.random_state)
    benchmark = save_benchmark(raw_path=args.raw, output_path=args.output, config=config)
    print(f"Wrote {len(benchmark)} benchmark rows to {args.output}")
    print(benchmark['split'].value_counts().to_string())


if __name__ == "__main__":
    main()
