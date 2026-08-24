from pathlib import Path

from benchmarks.phase8.runner import run_benchmark


def test_phase8_benchmark_metrics():
    payload = run_benchmark(persist=False)
    assert payload["passed"] is True
    assert not payload["failures"]
    assert payload["concepts"]["total"] >= 10
    assert Path(__file__).resolve().parents[2].joinpath("src/app/static/js/app.js").exists()
