from benchmarks.phase7.runner import run_benchmark


def test_phase7_benchmark_meets_targets():
    payload = run_benchmark(persist=False, seed=20260814)
    assert payload["passed"], payload["failures"]
    assert payload["catalog"]["subjects"] >= 1
    assert payload["catalog"]["concepts"] >= 10
    assert payload["counterfactual"]["preserved"] is True
    assert payload["determinism"]["identical"] is True
