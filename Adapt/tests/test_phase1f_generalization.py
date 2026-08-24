"""Generalization split, recovery, persistence, and determinism."""

from __future__ import annotations

from benchmarks.phase1f.evaluator import run_adapt
from benchmarks.phase1f.runner import comparable_payload, run_benchmark
from benchmarks.phase1f.scenarios import SCENARIO_BY_ID, split_scenarios


def test_recovery_scenario_can_improve_state():
    record = run_adapt(SCENARIO_BY_ID["G-005-A"])
    assert record["recovery_scenario"] is True
    assert record["recovered"] is True or record["decision"] != "REMEDIATE"


def test_persistent_misconception_changes_strategy():
    record = run_adapt(SCENARIO_BY_ID["G-006-A"])
    assert record["decision"] in {
        "REMEDIATE",
        "CHANGE_REPRESENTATION",
        "GATHER_MORE_EVIDENCE",
        "DECREASE_DIFFICULTY",
    }


def test_development_and_holdout_are_both_nonempty():
    assert split_scenarios("development")
    assert split_scenarios("holdout")


def test_benchmark_determinism():
    first = comparable_payload(run_benchmark(persist=False)["raw"])
    second = comparable_payload(run_benchmark(persist=False)["raw"])
    assert first["development"] == second["development"]
    assert first["holdout"] == second["holdout"]
    assert first["metamorphic"] == second["metamorphic"]
    assert first["longitudinal"] == second["longitudinal"]
