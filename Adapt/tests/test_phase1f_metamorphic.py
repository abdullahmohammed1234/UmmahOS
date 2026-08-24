"""Metamorphic relationship tests."""

from __future__ import annotations

from benchmarks.phase1f.metamorphic import run_metamorphic


def test_metamorphic_suite_runs_and_has_required_ids():
    results = run_metamorphic()
    ids = {item["test_id"] for item in results}
    assert ids == {"MT-001", "MT-002", "MT-003", "MT-004", "MT-005"}
    for item in results:
        assert "passed" in item
        assert "decision_a" in item


def test_mt005_instruction_does_not_override_decision():
    results = {item["test_id"]: item for item in run_metamorphic()}
    assert results["MT-005"]["passed"] is True
