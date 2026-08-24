"""Phase 1E scenario-suite contract tests."""

from __future__ import annotations

from benchmarks.phase1e.scenarios import SCENARIOS, counterfactual_pairs, scenario_steps


def test_minimum_scenario_counts():
    families = {item.family for item in SCENARIOS}
    assert "S-001" in families
    assert "S-012" in families
    assert len(families) >= 12
    assert len(SCENARIOS) >= 36
    pairs = counterfactual_pairs()
    dimensions = {members["A"].counterfactual_dimension for members in pairs.values()}
    assert len(pairs) >= 3
    assert "reasoning_quality" in dimensions
    assert "misconception" in dimensions
    assert "learner_confidence" in dimensions


def test_each_family_has_three_surface_variants_where_applicable():
    by_family: dict[str, set[str]] = {}
    for item in SCENARIOS:
        by_family.setdefault(item.family, set()).add(item.variant)
    for family in ("S-001", "S-002", "S-003", "S-004", "S-005", "S-006", "S-007", "S-008"):
        assert len(by_family[family]) >= 3


def test_expected_labels_are_present_but_not_in_system_inputs():
    for scenario in SCENARIOS:
        assert scenario.expected_decisions
        assert scenario.expected_adaptive_behavior
        steps = scenario_steps(scenario, "probe")
        challenge, response = steps[-1]
        payload = response.to_dict()
        assert "expected" not in payload
        assert "expected_decisions" not in payload
        assert scenario.expected_adaptive_behavior not in (response.answer or "")
        assert scenario.expected_adaptive_behavior not in (response.reasoning or "")


def test_counterfactual_pairs_are_complete():
    pairs = counterfactual_pairs()
    for pair_id, members in pairs.items():
        assert "A" in members and "B" in members
        assert members["A"].counterfactual_pair_id == pair_id
        assert members["A"].counterfactual_dimension == members["B"].counterfactual_dimension
        assert set(members["A"].expected_decisions) != set(members["B"].expected_decisions)
