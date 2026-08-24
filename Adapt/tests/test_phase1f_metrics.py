"""Phase 1F metric helper tests."""

from __future__ import annotations

from benchmarks.phase1e.metrics import appropriateness_rate
from benchmarks.phase1f.metrics import assign_band, development_holdout_gap


def test_perfect_zero_partial_and_empty():
    perfect = appropriateness_rate([{"appropriate": True}, {"appropriate": True}])
    zero = appropriateness_rate([{"appropriate": False}, {"appropriate": False}])
    partial = appropriateness_rate([{"appropriate": True}, {"appropriate": False}])
    empty = appropriateness_rate([])
    assert perfect["rate"] == 1.0
    assert zero["rate"] == 0.0
    assert abs(partial["rate"] - 0.5) < 1e-12
    assert empty["rate"] is None
    assert empty["wilson_95"] is None


def test_development_holdout_gap():
    gap = development_holdout_gap({"rate": 0.91}, {"rate": 0.87})
    assert abs(gap - 0.04) < 1e-12
    assert development_holdout_gap({"rate": None}, {"rate": 0.5}) is None


def test_assign_band_uses_frozen_thresholds():
    robust = assign_band(0.90, 0.05, {"metamorphic_rate": 1.0, "adversarial_no_override": True, "recovery_rate": 0.8})
    assert robust == "ROBUST"
    partial = assign_band(0.70, 0.10, {"metamorphic_rate": 0.5, "adversarial_no_override": True, "recovery_rate": 0.5})
    assert partial == "PARTIALLY_ROBUST"
    failed = assign_band(0.40, 0.30, {"metamorphic_rate": 0.2, "adversarial_no_override": False, "recovery_rate": 0.1})
    assert failed == "NOT_ROBUST"
