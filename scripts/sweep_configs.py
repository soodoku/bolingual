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

from hien_soundmatch.experiment import ExperimentConfig, evaluate_benchmark, summarize_results


def main() -> None:
    parser = argparse.ArgumentParser(description="Sweep a small grid of hybrid retrieval settings.")
    parser.add_argument("--benchmark", type=Path, default=Path("data/processed/benchmark.csv"))
    parser.add_argument("--output", type=Path, default=Path("results/config_sweep.csv"))
    parser.add_argument("--split", type=str, default="test")
    args = parser.parse_args()

    benchmark = pd.read_csv(args.benchmark)
    rows = []
    for top_k, alpha in [(50, 0.35), (50, 0.5), (50, 0.65), (100, 0.5), (200, 0.5)]:
        config = ExperimentConfig(top_k=top_k, alpha=alpha, schwa_cost=0.3)
        results = evaluate_benchmark(benchmark=benchmark, split=args.split, config=config)
        summary = summarize_results(results)
        overall = summary["overall"]["hybrid_topk"]
        hard = summary["hard_subset"]["hybrid_topk"]
        rows.append(
            {
                "top_k": top_k,
                "alpha": alpha,
                "top1": overall["top1"],
                "top5": overall["top5"],
                "top10": overall["top10"],
                "mrr": overall["mrr"],
                "hard_top1": hard["top1"],
                "hard_mrr": hard["mrr"],
            }
        )
        print(rows[-1])
    output = pd.DataFrame(rows).sort_values(["top1", "mrr"], ascending=[False, False])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(args.output, index=False)
    print(f"Wrote sweep results to {args.output}")


if __name__ == "__main__":
    main()
