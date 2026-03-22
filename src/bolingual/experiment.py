from __future__ import annotations

import json
import math
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from .models import CandidateIndex


@dataclass(frozen=True)
class ExperimentConfig:
    top_k: int = 200
    alpha: float = 0.5
    schwa_cost: float = 0.3


DEFAULT_EXPERIMENT = ExperimentConfig()


def rank_of_word(ranking: Iterable[tuple[float, str]], gold: str) -> float:
    for rank, (_, word) in enumerate(ranking, start=1):
        if word == gold:
            return float(rank)
    return math.inf


def metrics_from_ranks(ranks: pd.Series) -> dict[str, float]:
    finite = ranks.apply(lambda value: 0.0 if value == math.inf else 1.0 / float(value))
    return {
        "top1": float((ranks <= 1).mean()),
        "top5": float((ranks <= 5).mean()),
        "top10": float((ranks <= 10).mean()),
        "mrr": float(finite.mean()),
    }


def summarize_results(results: pd.DataFrame) -> dict[str, Any]:
    overall = {
        "orthographic": metrics_from_ranks(results["orth_rank"]),
        "phonetic_topk": metrics_from_ranks(results["phonetic_rank"]),
        "hybrid_topk": metrics_from_ranks(results["hybrid_rank"]),
    }
    hard = results[results["hard"]].copy()
    hard_summary: dict[str, Any] = {
        "n": int(len(hard)),
        "orthographic": metrics_from_ranks(hard["orth_rank"]),
        "phonetic_topk": metrics_from_ranks(hard["phonetic_rank"]),
        "hybrid_topk": metrics_from_ranks(hard["hybrid_rank"]),
    }
    return {
        "n": int(len(results)),
        "overall": overall,
        "hard_subset": hard_summary,
    }


def evaluate_benchmark(
    benchmark: pd.DataFrame,
    split: str = "test",
    config: ExperimentConfig = DEFAULT_EXPERIMENT,
) -> pd.DataFrame:
    eval_rows = benchmark[benchmark["split"] == split].copy().reset_index(drop=True)
    index = CandidateIndex.from_words(benchmark["gold"].unique())
    outputs: list[dict[str, object]] = []

    for _, row in eval_rows.iterrows():
        rankings = index.hybrid_ranking(
            hindi_text=str(row["hindi"]),
            top_k=config.top_k,
            alpha=config.alpha,
            schwa_cost=config.schwa_cost,
        )
        orthographic = rankings["orthographic"]
        phonetic = rankings["phonetic"]
        hybrid = rankings["hybrid"]
        outputs.append(
            {
                "hindi": row["hindi"],
                "gold": row["gold"],
                "votes": int(row["votes"]),
                "total_votes": int(row["total_votes"]),
                "q_raw": row["q_raw"],
                "q_coarse": row["q_coarse"],
                "hard": bool(row["hard"]),
                "orth_rank": rank_of_word(orthographic, str(row["gold"])),
                "phonetic_rank": rank_of_word(phonetic, str(row["gold"])),
                "hybrid_rank": rank_of_word(hybrid, str(row["gold"])),
                "orth_top5": "|".join(word for _, word in orthographic[:5]),
                "phonetic_top5": "|".join(word for _, word in phonetic[:5]),
                "hybrid_top5": "|".join(word for _, word in hybrid[:5]),
            }
        )
    return pd.DataFrame(outputs)


def select_improvement_examples(results: pd.DataFrame, limit: int = 15) -> pd.DataFrame:
    subset = results[(results["orth_rank"] > 5) & (results["hybrid_rank"] <= 3)].copy()
    subset = subset.sort_values(
        ["hybrid_rank", "orth_rank", "hindi"], ascending=[True, False, True]
    )
    return subset.head(limit).reset_index(drop=True)


def write_markdown_report(
    benchmark: pd.DataFrame,
    results: pd.DataFrame,
    summary: dict[str, Any],
    output_path: str | Path,
    config: ExperimentConfig = DEFAULT_EXPERIMENT,
) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    overall: dict[str, Any] = summary["overall"]
    hard: dict[str, Any] = summary["hard_subset"]
    examples = select_improvement_examples(results, limit=10)
    lines: list[str] = []
    lines.append("# Hindi-English sound matching experiment\n")
    lines.append(f"Benchmark size: **{len(benchmark)}** items")
    lines.append(
        f"Dev/Test split: **{int((benchmark['split'] == 'dev').sum())} / {int((benchmark['split'] == 'test').sum())}**"
    )
    lines.append(f"Unique English candidate words: **{benchmark['gold'].nunique()}**")
    lines.append(
        f"Experiment config: top_k={config.top_k}, alpha={config.alpha}, schwa_cost={config.schwa_cost}\n"
    )
    lines.append("## Test metrics\n")
    lines.append("| method | top1 | top5 | top10 | mrr |")
    lines.append("|---|---:|---:|---:|---:|")
    for key, label in [
        ("orthographic", "Orthographic"),
        ("phonetic_topk", f"Phonetic top-{config.top_k}"),
        ("hybrid_topk", f"Hybrid top-{config.top_k}"),
    ]:
        metric: dict[str, float] = overall[key]
        lines.append(
            f"| {label} | {metric['top1']:.3f} | {metric['top5']:.3f} | {metric['top10']:.3f} | {metric['mrr']:.3f} |"
        )
    lines.append("\n## Hard subset\n")
    lines.append(f"Hard subset size: **{hard['n']}**")
    lines.append("| method | top1 | top5 | top10 | mrr |")
    lines.append("|---|---:|---:|---:|---:|")
    for key, label in [
        ("orthographic", "Orthographic"),
        ("phonetic_topk", f"Phonetic top-{config.top_k}"),
        ("hybrid_topk", f"Hybrid top-{config.top_k}"),
    ]:
        metric = hard[key]
        lines.append(
            f"| {label} | {metric['top1']:.3f} | {metric['top5']:.3f} | {metric['top10']:.3f} | {metric['mrr']:.3f} |"
        )
    if not examples.empty:
        lines.append("\n## Example improvements\n")
        for _, row in examples.iterrows():
            lines.append(
                f"- **{row['hindi']}** → gold `{row['gold']}`; orth rank {int(row['orth_rank'])}, hybrid rank {int(row['hybrid_rank'])}; hybrid top5: {row['hybrid_top5']}"
            )
    output_path.write_text("\n".join(lines), encoding="utf-8")


def save_experiment_outputs(
    benchmark: pd.DataFrame,
    results: pd.DataFrame,
    output_dir: str | Path,
    config: ExperimentConfig = DEFAULT_EXPERIMENT,
) -> dict[str, Any]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = summarize_results(results)
    results.to_csv(output_dir / "test_results.csv", index=False)
    select_improvement_examples(results, limit=15).to_csv(
        output_dir / "example_improvements.csv", index=False
    )
    with (output_dir / "metrics_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2)
    with (output_dir / "config.json").open("w", encoding="utf-8") as handle:
        json.dump(
            {"top_k": config.top_k, "alpha": config.alpha, "schwa_cost": config.schwa_cost},
            handle,
            ensure_ascii=False,
            indent=2,
        )
    write_markdown_report(benchmark, results, summary, output_dir / "report.md", config=config)
    return summary
