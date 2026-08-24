"""Phase 3 metric and benchmark structure tests."""

from __future__ import annotations

import pytest

from benchmarks.phase3.constants import RANDOM_SEED
from benchmarks.phase3.expected import HOLDOUT_IDS, REQUIRED_TRAJECTORIES
from benchmarks.phase3.execute import run_scenario
from benchmarks.phase3.metrics import compute_metrics
from benchmarks.phase3.scenarios import SCENARIOS, development_scenarios, holdout_scenarios
from benchmarks.phase3.trajectories import TRAJECTORIES
from tests.helpers_phase3 import make_tutor


def test_holdout_is_frozen_and_separated():
    ids = {item.scenario_id for item in SCENARIOS} | {item.trajectory_id for item in TRAJECTORIES}
    assert HOLDOUT_IDS.issubset(ids)
    assert all(item.split == "holdout" for item in holdout_scenarios())
    assert all(item.split == "development" for item in development_scenarios())
    total = len(SCENARIOS) + len(TRAJECTORIES)
    holdout_n = sum(1 for item in SCENARIOS if item.split == "holdout") + sum(
        1 for item in TRAJECTORIES if item.split == "holdout"
    )
    assert 0.25 <= holdout_n / total <= 0.40


def test_required_trajectories_exist_and_are_long():
    ids = {item.trajectory_id for item in TRAJECTORIES}
    assert set(REQUIRED_TRAJECTORIES).issubset(ids)
    for item in TRAJECTORIES:
        if item.trajectory_id in REQUIRED_TRAJECTORIES:
            assert item.n_steps >= 20


def test_scored_steps_exceed_80():
    session_steps = sum(item.n_steps for item in SCENARIOS)
    traj_steps = sum(item.n_steps for item in TRAJECTORIES)
    assert session_steps + traj_steps >= 80
    assert len(SCENARIOS) + len(TRAJECTORIES) >= 20
    assert len(TRAJECTORIES) >= 6


def test_seed_is_recorded():
    assert RANDOM_SEED == 20260814


def test_metrics_keys_exist():
    tutor = make_tutor()
    record = run_scenario(next(item for item in SCENARIOS if item.scenario_id == "S-001"), tutor=tutor)
    metrics = compute_metrics([record], [])
    for key in (
        "M3-001_end_to_end_adaptation",
        "M3-002_state_to_strategy_causality",
        "M3-003_strategy_to_challenge_consistency",
        "M3-004_counterfactual_differentiation",
        "M3-005_longitudinal_stability",
        "M3-006_recovery",
        "M3-007_misconception_handling",
        "M3-008_trace_completeness",
    ):
        assert key in metrics


def test_s001_is_appropriate():
    record = run_scenario(next(item for item in SCENARIOS if item.scenario_id == "S-001"))
    assert record["trace_complete_rate"] == 1.0
    assert record["n_steps"] == 4


def test_counterfactual_pair_records_exist():
    ids = {item.scenario_id for item in SCENARIOS}
    assert {"P3-CF-001A", "P3-CF-001B", "P3-CF-002A", "P3-CF-002B", "P3-CF-003A", "P3-CF-003B"} <= ids


@pytest.mark.parametrize("scenario_id", [item.scenario_id for item in SCENARIOS])
def test_each_scenario_executes_with_complete_traces(scenario_id: str):
    from benchmarks.phase3.scenarios import SCENARIO_BY_ID

    record = run_scenario(SCENARIO_BY_ID[scenario_id])
    assert record["n_steps"] >= 1
    assert record["trace_complete_rate"] == 1.0
    assert record["final_strategy"]
    assert record["final_challenge_id"]


@pytest.mark.parametrize("trajectory_id", [item.trajectory_id for item in TRAJECTORIES])
def test_each_trajectory_executes(trajectory_id: str):
    from benchmarks.phase3.execute import run_trajectory
    from benchmarks.phase3.trajectories import TRAJECTORY_BY_ID

    record = run_trajectory(TRAJECTORY_BY_ID[trajectory_id])
    assert record["n_steps"] >= 20
    assert record["trace_complete_rate"] == 1.0
    assert not record["oscillation_violation"] or trajectory_id not in REQUIRED_TRAJECTORIES

