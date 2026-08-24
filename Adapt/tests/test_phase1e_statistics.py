"""Statistical helper tests."""

from __future__ import annotations

from benchmarks.phase1e.statistics import (
    mcnemar_test,
    percentage_point_difference,
    relative_improvement,
    wilson_interval,
)


def test_wilson_interval_bounds_and_known_case():
    interval = wilson_interval(10, 10)
    assert interval is not None
    low, high = interval
    assert 0.0 <= low <= high <= 1.0
    assert high == 1.0 or high < 1.0
    small = wilson_interval(1, 2)
    assert small is not None
    assert small[0] < 0.5 < small[1]


def test_wilson_zero_n():
    assert wilson_interval(0, 0) is None


def test_percentage_points_and_relative():
    assert percentage_point_difference(0.9, 0.633) == (0.9 - 0.633) * 100
    assert abs(relative_improvement(0.9, 0.6) - 0.5) < 1e-12
    assert relative_improvement(0.4, 0.0) is None
    assert relative_improvement(None, 0.5) is None


def test_mcnemar_no_discordant_and_discordant():
    none = mcnemar_test(0, 0)
    assert none["p_value"] == 1.0
    some = mcnemar_test(8, 2)
    assert some["statistic"] > 0
    assert 0.0 < some["p_value"] < 1.0


def test_statistics_are_deterministic():
    first = wilson_interval(27, 30)
    second = wilson_interval(27, 30)
    assert first == second
    assert mcnemar_test(5, 1) == mcnemar_test(5, 1)
