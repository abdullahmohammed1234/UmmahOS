from benchmarks.phase9.runner import run_benchmark


def test_phase9_benchmark_passes_without_persist():
    payload = run_benchmark(persist=False)
    assert payload["pass"] is True
    assert payload["failures"] == []
