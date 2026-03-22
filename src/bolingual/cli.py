"""Command-line interface for bolingual."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .benchmarking import BenchmarkConfig, save_benchmark
from .experiment import ExperimentConfig, evaluate_benchmark, save_experiment_outputs
from .models import CandidateIndex


def build_benchmark_cli() -> None:
    """CLI entry point for building the benchmark."""
    parser = argparse.ArgumentParser(
        description="Build the Hindi-English sound-matching benchmark."
    )
    parser.add_argument(
        "--raw",
        type=Path,
        default=Path("data/raw/crowd_transliterations.hi-en.txt"),
        help="Path to raw Xlit-Crowd data",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/benchmark.csv"),
        help="Output path for benchmark CSV",
    )
    parser.add_argument("--test-fraction", type=float, default=0.25)
    parser.add_argument("--random-state", type=int, default=42)
    args = parser.parse_args()

    config = BenchmarkConfig(test_fraction=args.test_fraction, random_state=args.random_state)
    benchmark = save_benchmark(raw_path=args.raw, output_path=args.output, config=config)
    print(f"Wrote {len(benchmark)} benchmark rows to {args.output}")
    print(benchmark["split"].value_counts().to_string())


def run_experiment_cli() -> None:
    """CLI entry point for running experiments."""
    parser = argparse.ArgumentParser(description="Run the retrieval experiment on the benchmark.")
    parser.add_argument(
        "--benchmark",
        type=Path,
        default=Path("data/processed/benchmark.csv"),
        help="Path to benchmark CSV",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results"),
        help="Output directory for results",
    )
    parser.add_argument("--split", type=str, default="test")
    parser.add_argument("--top-k", type=int, default=200)
    parser.add_argument("--alpha", type=float, default=0.5)
    parser.add_argument("--schwa-cost", type=float, default=0.3)
    args = parser.parse_args()

    benchmark = pd.read_csv(args.benchmark)
    config = ExperimentConfig(top_k=args.top_k, alpha=args.alpha, schwa_cost=args.schwa_cost)
    results = evaluate_benchmark(benchmark=benchmark, split=args.split, config=config)
    summary = save_experiment_outputs(
        benchmark=benchmark, results=results, output_dir=args.output_dir, config=config
    )
    print(summary)
    print(f"Wrote experiment outputs to {args.output_dir}")


def query_cli() -> None:
    """CLI entry point for interactive queries."""
    parser = argparse.ArgumentParser(description="Query the hybrid Hindi-English sound matcher.")
    parser.add_argument(
        "--benchmark",
        type=Path,
        default=Path("data/processed/benchmark.csv"),
        help="Path to benchmark CSV",
    )
    parser.add_argument("--hindi", type=str, required=True, help="Hindi word to query")
    parser.add_argument("--top-k", type=int, default=200)
    parser.add_argument("--alpha", type=float, default=0.5)
    parser.add_argument("--show", type=int, default=10, help="Number of results to show")
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
