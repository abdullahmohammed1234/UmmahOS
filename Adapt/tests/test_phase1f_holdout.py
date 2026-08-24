"""Holdout integrity tests."""

from __future__ import annotations

from benchmarks.phase1f.holdout import HOLDOUT_IDS
from benchmarks.phase1f.scenarios import SCENARIO_BY_ID, split_scenarios


def test_every_holdout_id_exists():
    for scenario_id in HOLDOUT_IDS:
        assert scenario_id in SCENARIO_BY_ID
        assert SCENARIO_BY_ID[scenario_id].split == "holdout"


def test_development_contains_no_holdout_id():
    development_ids = {item.scenario_id for item in split_scenarios("development")}
    assert development_ids.isdisjoint(HOLDOUT_IDS)


def test_holdout_fraction_near_thirty_percent():
    total = len(SCENARIO_BY_ID)
    holdout = len(HOLDOUT_IDS)
    assert 0.25 <= holdout / total <= 0.40
