from pathlib import Path

from bolingual.benchmarking import build_benchmark_dataframe
from bolingual.phonetics import coarse_match_key_for_hindi, hindi_variants, romanize_hindi


def test_basic_romanization() -> None:
    assert romanize_hindi("वॉटसन")
    assert coarse_match_key_for_hindi("वॉटसन")
    assert len(hindi_variants("वॉटसन")) >= 1


def test_benchmark_build(tmp_path: Path) -> None:
    raw_path = Path(__file__).resolve().parents[1] / "data/raw/crowd_transliterations.hi-en.txt"
    benchmark = build_benchmark_dataframe(raw_path)
    assert len(benchmark) > 2000
    assert set(benchmark["split"]) == {"dev", "test"}
