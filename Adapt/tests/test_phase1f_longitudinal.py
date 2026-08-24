"""Longitudinal trajectory tests."""

from __future__ import annotations

from benchmarks.phase1f.longitudinal import TRAJECTORIES, run_longitudinal


def test_five_trajectories_of_at_least_twenty_steps():
    assert len(TRAJECTORIES) >= 5
    results = run_longitudinal()
    assert len(results) >= 5
    for item in results:
        assert item["steps"] >= 20
        assert item["traceable"] is True
        assert 0.0 <= item["final_mastery"] <= 1.0
