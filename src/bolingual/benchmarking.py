from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .phonetics import (
    clean_english,
    cmudict_entries,
    coarse_match_key_for_english,
    coarse_match_key_for_hindi,
    romanize_hindi,
)


@dataclass(frozen=True)
class BenchmarkConfig:
    test_fraction: float = 0.25
    random_state: int = 42


DEFAULT_CONFIG = BenchmarkConfig()


def load_raw_pairs(path: str | Path) -> pd.DataFrame:
    data = pd.read_csv(path, sep="\t", names=["en_raw", "hindi"], dtype=str)
    data["english"] = data["en_raw"].map(clean_english)
    data = data[data["english"] != ""].copy()
    return data


def build_benchmark_dataframe(
    raw_path: str | Path, config: BenchmarkConfig = DEFAULT_CONFIG
) -> pd.DataFrame:
    cmu = cmudict_entries()
    raw_pairs = load_raw_pairs(raw_path)
    grouped = raw_pairs.groupby(["hindi", "english"]).size().reset_index(name="votes")

    rows: list[dict[str, object]] = []
    for hindi_key, group in grouped.groupby("hindi", sort=True):
        hindi = str(hindi_key)
        ordered = group.sort_values(["votes", "english"], ascending=[False, True]).reset_index(
            drop=True
        )
        top = ordered.iloc[0]
        gold = str(top["english"])
        if gold not in cmu:
            continue
        total_votes = int(ordered["votes"].sum())
        q_raw = romanize_hindi(hindi)
        q_coarse = coarse_match_key_for_hindi(hindi)
        gold_coarse = coarse_match_key_for_english(gold)
        rows.append(
            {
                "hindi": hindi,
                "gold": gold,
                "votes": int(top["votes"]),
                "total_votes": total_votes,
                "q_raw": q_raw,
                "q_coarse": q_coarse,
                "hard": q_coarse != gold_coarse,
            }
        )

    benchmark = pd.DataFrame(rows).sort_values(["hindi", "gold"]).reset_index(drop=True)
    num_test = int(round(len(benchmark) * config.test_fraction))
    rng = np.random.default_rng(config.random_state)
    indices = np.arange(len(benchmark))
    rng.shuffle(indices)
    split = np.full(len(benchmark), "dev", dtype=object)
    split[indices[:num_test]] = "test"
    benchmark["split"] = split
    return benchmark


def save_benchmark(
    raw_path: str | Path, output_path: str | Path, config: BenchmarkConfig = DEFAULT_CONFIG
) -> pd.DataFrame:
    benchmark = build_benchmark_dataframe(raw_path=raw_path, config=config)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    benchmark.to_csv(output_path, index=False)
    return benchmark
