#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="$ROOT_DIR/src:${PYTHONPATH:-}"

python scripts/build_benchmark.py \
  --raw data/raw/crowd_transliterations.hi-en.txt \
  --output data/processed/benchmark.csv \
  --test-fraction 0.25 \
  --random-state 42

python scripts/run_experiment.py \
  --benchmark data/processed/benchmark.csv \
  --output-dir results \
  --split test \
  --top-k 200 \
  --alpha 0.5 \
  --schwa-cost 0.3
