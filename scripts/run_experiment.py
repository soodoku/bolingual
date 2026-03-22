#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import pandas as pd

from hien_soundmatch.experiment import ExperimentConfig, evaluate_benchmark, save_experiment_outputs


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the retrieval experiment on the benchmark.")
    parser.add_argument("--benchmark", type=Path, default=Path("data/processed/benchmark.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("results"))
    parser.add_argument("--split", type=str, default="test")
    parser.add_argument("--top-k", type=int, default=200)
    parser.add_argument("--alpha", type=float, default=0.5)
    parser.add_argument("--schwa-cost", type=float, default=0.3)
    args = parser.parse_args()

    benchmark = pd.read_csv(args.benchmark)
    config = ExperimentConfig(top_k=args.top_k, alpha=args.alpha, schwa_cost=args.schwa_cost)
    results = evaluate_benchmark(benchmark=benchmark, split=args.split, config=config)
    summary = save_experiment_outputs(benchmark=benchmark, results=results, output_dir=args.output_dir, config=config)
    print(summary)
    print(f"Wrote experiment outputs to {args.output_dir}")


if __name__ == "__main__":
    main()
