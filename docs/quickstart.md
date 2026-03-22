# Quickstart

## Installation

```bash
pip install bolingual
```

Or with uv:

```bash
uv add bolingual
```

## Basic Usage

### Finding Similar-Sounding English Words

```python
from bolingual import CandidateIndex

# Build index from English word list
index = CandidateIndex.from_cmudict()

# Query with Hindi word
results = index.hybrid_ranking("वॉटसन", top_k=5)
for word, score in results:
    print(f"{word}: {score:.3f}")
```

### Building the Benchmark

```python
from pathlib import Path
from bolingual import build_benchmark_dataframe

benchmark = build_benchmark_dataframe(Path("data/raw/crowd_transliterations.hi-en.txt"))
print(f"Total items: {len(benchmark)}")
print(f"Dev/Test split: {benchmark['split'].value_counts().to_dict()}")
```

### Running Experiments

```python
from bolingual import CandidateIndex, evaluate_benchmark, summarize_results

index = CandidateIndex.from_cmudict()
results = evaluate_benchmark(benchmark, index, split="test")
metrics = summarize_results(results)
print(metrics)
```

## Command Line Interface

Build the benchmark:

```bash
bolingual-build-benchmark --raw data/raw/crowd_transliterations.hi-en.txt --output benchmark.csv
```

Run experiments:

```bash
bolingual-run-experiment --benchmark benchmark.csv --output-dir results/
```

Interactive query:

```bash
bolingual-query --hindi "वॉटसन" --show 10
```
