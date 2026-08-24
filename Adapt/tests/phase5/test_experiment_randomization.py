"""Condition assignment is deterministic and balances order."""

from __future__ import annotations

from adapt.eval.protocol import assign_condition_order, assign_group, next_participant_id


def test_p001_is_adapt_first_with_frozen_seed():
    assert assign_condition_order("P001") == ["ADAPT", "BASELINE"]
    assert assign_group("P001") == "group_1_adapt_first"


def test_p002_is_baseline_first_with_frozen_seed():
    assert assign_condition_order("P002") == ["BASELINE", "ADAPT"]
    assert assign_group("P002") == "group_2_baseline_first"


def test_assignment_is_deterministic():
    first = [assign_condition_order(f"P{i:03d}") for i in range(1, 11)]
    second = [assign_condition_order(f"P{i:03d}") for i in range(1, 11)]
    assert first == second
    adapt_first = sum(1 for order in first if order[0] == "ADAPT")
    assert adapt_first == 5


def test_next_participant_id_fills_gaps():
    assert next_participant_id([]) == "P001"
    assert next_participant_id(["P001", "P003"]) == "P002"
