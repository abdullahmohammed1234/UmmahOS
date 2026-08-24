"""Phase 1E evaluator and reproducibility tests."""

from __future__ import annotations

from benchmarks.phase1e.evaluator import evaluate_suite, run_adapt, run_baseline
from benchmarks.phase1e.normalization import normalize_decision
from benchmarks.phase1e.runner import comparable_payload, run_benchmark
from benchmarks.phase1e.scenarios import SCENARIO_BY_ID


def test_normalization_aliases_and_unknown():
    assert normalize_decision("make harder") == "INCREASE_DIFFICULTY"
    assert normalize_decision("remediate misconception") == "REMEDIATE"
    assert normalize_decision("ask another diagnostic question") == "GATHER_MORE_EVIDENCE"
    assert normalize_decision("INCREASE_DIFFICULTY") == "INCREASE_DIFFICULTY"
    unknown = normalize_decision("because the AI thinks so")
    assert unknown.startswith("UNMAPPED:")


def test_adapt_and_baseline_receive_same_scenario_payload():
    scenario = SCENARIO_BY_ID["S-002-A"]
    adapt = run_adapt(scenario)
    baseline = run_baseline(scenario)
    assert adapt["scenario_id"] == baseline["scenario_id"] == scenario.scenario_id
    assert baseline["learner_state_after"] is None
    assert baseline["evidence"] is None
    assert adapt["learner_state_after"] is not None
    assert adapt["evidence"] is not None


def test_baseline_does_not_fabricate_adapt_state():
    record = run_baseline(SCENARIO_BY_ID["S-001-A"])
    assert record["learner_state_before"] is None
    assert record["decision_trace"] is None
    assert record["traceable"] is False


def test_reproducibility_two_in_memory_runs_match():
    first = comparable_payload(run_benchmark(persist=False)["raw"])
    second = comparable_payload(run_benchmark(persist=False)["raw"])
    assert first["adapt_records"] == second["adapt_records"]
    assert first["baseline_records"] == second["baseline_records"]
    assert first["adapt_pairs"] == second["adapt_pairs"]


def test_evaluate_suite_has_paired_records():
    evaluation = evaluate_suite()
    assert len(evaluation["paired"]) == len(evaluation["adapt_records"])
    assert evaluation["paired"][0]["adapt"]["scenario_id"] == evaluation["paired"][0]["baseline"]["scenario_id"]
