"""Independent metric-function tests."""

from __future__ import annotations

from benchmarks.phase1e.metrics import (
    appropriateness_rate,
    binary_flag_rate,
    compare_systems,
    counterfactual_differentiation_rate,
    paired_mcnemar,
)


def test_appropriateness_three_of_four():
    records = [
        {"appropriate": True},
        {"appropriate": True},
        {"appropriate": True},
        {"appropriate": False},
    ]
    result = appropriateness_rate(records)
    assert result["numerator"] == 3
    assert result["denominator"] == 4
    assert abs(result["rate"] - 0.75) < 1e-12


def test_counterfactual_two_of_three():
    pairs = [
        {"differentiated": True},
        {"differentiated": True},
        {"differentiated": False},
    ]
    result = counterfactual_differentiation_rate(pairs)
    assert result["numerator"] == 2
    assert result["denominator"] == 3
    assert abs(result["rate"] - (2 / 3)) < 1e-12


def test_zero_denominator_does_not_crash():
    empty = appropriateness_rate([])
    assert empty["denominator"] == 0
    assert empty["rate"] is None
    assert empty["wilson_95"] is None


def test_perfect_and_zero_scores():
    perfect = binary_flag_rate([{"traceable": True}, {"traceable": True}], "traceable")
    zero = binary_flag_rate([{"traceable": False}, {"traceable": False}], "traceable")
    assert perfect["rate"] == 1.0
    assert zero["rate"] == 0.0


def test_missing_optional_fields():
    records = [{"appropriate": True}, {}]
    result = appropriateness_rate(records)
    assert result["numerator"] == 1
    paired = [
        {"adapt": {"appropriate": True}, "baseline": {}},
        {"adapt": {}, "baseline": {"appropriate": True}},
    ]
    table = paired_mcnemar(paired)
    assert table["n10"] == 1
    assert table["n01"] == 1


def test_compare_systems_relative_improvement():
    comparison = compare_systems(
        {"rate": 0.9, "display": "9 / 10 = 90.0%"},
        {"rate": 0.6, "display": "6 / 10 = 60.0%"},
    )
    assert abs(comparison["percentage_point_difference"] - 30.0) < 1e-9
    assert abs(comparison["relative_improvement"] - 0.5) < 1e-9
    zero_base = compare_systems({"rate": 0.5}, {"rate": 0.0})
    assert zero_base["relative_improvement"] is None
