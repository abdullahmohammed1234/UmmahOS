"""Phase 1F scenario contract tests."""

from __future__ import annotations

from benchmarks.phase1f.holdout import HOLDOUT_IDS
from benchmarks.phase1f.scenarios import SCENARIOS, scenario_steps, split_scenarios


def test_family_and_count_minimums():
    families = {item.family for item in SCENARIOS}
    assert len(families) >= 15
    assert len(SCENARIOS) >= 45
    for family in [f"G-{i:03d}" for i in range(1, 16)]:
        assert family in families


def test_required_scenario_fields():
    for item in SCENARIOS:
        assert item.scenario_id
        assert item.concept
        assert item.current_challenge_id
        assert item.expected_adaptive_behavior
        assert item.expected_decisions
        assert item.category
        assert item.split in {"development", "holdout"}
        steps = scenario_steps(item, "probe")
        assert steps
        payload = steps[-1][1].to_dict()
        assert "expected_decisions" not in payload


def test_novelty_and_multi_dimension_quotas():
    novel = [item for item in SCENARIOS if item.novel]
    multi = [item for item in SCENARIOS if item.multi_dimension]
    assert len(novel) / len(SCENARIOS) >= 0.5
    assert len(multi) / len(SCENARIOS) >= 0.3


def test_holdout_is_disjoint_and_frozen():
    development = {item.scenario_id for item in split_scenarios("development")}
    holdout = {item.scenario_id for item in split_scenarios("holdout")}
    assert development.isdisjoint(holdout)
    assert holdout == set(HOLDOUT_IDS)
    assert all(item.scenario_id in {s.scenario_id for s in SCENARIOS} for item in split_scenarios("holdout"))
