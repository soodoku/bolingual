# bolingual

[![PyPI](https://img.shields.io/pypi/v/bolingual.svg)](https://pypi.org/project/bolingual/)
[![Python](https://img.shields.io/pypi/pyversions/bolingual.svg)](https://pypi.org/project/bolingual/)
[![CI](https://github.com/soodoku/bolingual/actions/workflows/ci.yml/badge.svg)](https://github.com/soodoku/bolingual/actions/workflows/ci.yml)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://soodoku.github.io/bolingual)

Reproducible Hindi-English sound-matching benchmark and retrieval baselines.

<!-- docs-intro-start -->
Find English words that sound similar to Hindi words written in Devanagari. The package includes:
- A curated benchmark of 2,959 Hindi-English pairs from Xlit-Crowd
- Three retrieval methods: orthographic, phonetic, and hybrid
- CLI tools and Python API for evaluation and querying
<!-- docs-intro-end -->

## Installation

```bash
pip install bolingual
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add bolingual
```

### Streamlit App

To use the interactive web app:

```bash
pip install bolingual[app]
```

Then run:

```bash
bolingual-app
```

Or directly with streamlit:

```bash
streamlit run src/bolingual/app.py
```

## Method Comparison

Evaluation on held-out test set (740 items, top_k=200, alpha=0.5):

| Method | Top-1 | Top-5 | Top-10 | MRR |
|--------|------:|------:|-------:|----:|
| Orthographic | 53.1% | 70.1% | 74.3% | 0.609 |
| Phonetic | 61.9% | 79.1% | 82.3% | 0.694 |
| **Hybrid** | **70.3%** | **82.0%** | **84.2%** | **0.757** |

On "hard" examples where orthographic keys don't match (216 items):

| Method | Top-1 | Top-5 | MRR |
|--------|------:|------:|----:|
| Orthographic | 21.8% | 42.1% | 0.318 |
| Phonetic | 52.3% | 74.1% | 0.615 |
| **Hybrid** | **66.7%** | **80.1%** | **0.725** |

### Where Hybrid Shines

| Hindi | Gold | Orthographic Rank | Hybrid Rank |
|-------|------|------------------:|------------:|
| सर्किट्स | circuits | 164 | 1 |
| न्यू | new | 122 | 1 |
| थैचर | thatcher | 116 | 1 |
| गेट | gate | 90 | 1 |
| फ्रॉस्ट | frost | 87 | 1 |

## Quick Start

```python
from bolingual import CandidateIndex

# Build index from benchmark vocabulary
import pandas as pd
benchmark = pd.read_csv("data/processed/benchmark.csv")
index = CandidateIndex.from_words(benchmark["gold"].unique())

# Query with Hindi word
rankings = index.hybrid_ranking("वॉटसन", top_k=200)
for score, word in rankings["hybrid"][:5]:
    print(f"{word}: {score:.3f}")
```

## CLI Usage

Build benchmark:
```bash
bolingual-build-benchmark --raw data/raw/crowd_transliterations.hi-en.txt --output benchmark.csv
```

Run experiments:
```bash
bolingual-run-experiment --benchmark benchmark.csv --output-dir results/
```

Query interactively:
```bash
bolingual-query --hindi "वॉटसन" --show 10
```

## How It Works

1. **Orthographic**: Romanize Hindi → normalize to coarse keys → rank with Jaro-Winkler similarity
2. **Phonetic**: Rerank orthographic shortlist using weighted edit distance over Hindi pronunciation variants and CMUdict pronunciations
3. **Hybrid**: Combine orthographic and phonetic scores (α=0.5 weighting)

Key features:
- Hindi schwa deletion handling (multiple pronunciation variants)
- Phonetic similarity groups for soft consonant/vowel matching
- CMUdict-backed English pronunciations

## Benchmark Details

- **Source**: Xlit-Crowd Hindi-English transliteration data
- **Size**: 2,959 items (2,219 dev / 740 test)
- **Vocabulary**: 2,673 unique English words
- **Construction**: Deterministic pipeline with CMUdict filtering

## Development

```bash
git clone https://github.com/soodoku/bolingual
cd bolingual
uv sync --all-extras
uv run pytest
uv run ruff check src tests
```

## License

MIT
