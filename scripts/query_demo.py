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

from hien_soundmatch.models import CandidateIndex


def main() -> None:
    parser = argparse.ArgumentParser(description="Query the hybrid Hindi-English sound matcher.")
    parser.add_argument("--benchmark", type=Path, default=Path("data/processed/benchmark.csv"))
    parser.add_argument("--hindi", type=str, required=True)
    parser.add_argument("--top-k", type=int, default=200)
    parser.add_argument("--alpha", type=float, default=0.5)
    parser.add_argument("--show", type=int, default=10)
    args = parser.parse_args()

    benchmark = pd.read_csv(args.benchmark)
    index = CandidateIndex.from_words(benchmark["gold"].unique())
    rankings = index.hybrid_ranking(hindi_text=args.hindi, top_k=args.top_k, alpha=args.alpha)
    print("Orthographic top candidates:")
    for rank, (score, word) in enumerate(rankings["orthographic"][: args.show], start=1):
        print(f"{rank:2d}. {word:20s} score={score:.3f}")
    print("\nHybrid top candidates:")
    for rank, (score, word) in enumerate(rankings["hybrid"][: args.show], start=1):
        print(f"{rank:2d}. {word:20s} score={score:.3f}")


if __name__ == "__main__":
    main()
