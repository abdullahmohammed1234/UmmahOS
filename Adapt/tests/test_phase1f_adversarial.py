"""Adversarial input tests."""

from __future__ import annotations

from benchmarks.phase1f.adversarial import run_adversarial


def test_adversarial_suite_does_not_crash_and_blocks_override():
    results = {item["test_id"]: item for item in run_adversarial()}
    assert results["ADV-expert-instruction"]["passed"] is True
    assert results["ADV-mark-mastered"]["passed"] is True
    assert results["ADV-ignore-history"]["passed"] is True
    assert results["ADV-tiny-response"]["passed"] is True
    assert results["ADV-very-long-response"]["passed"] is True
    assert results["ADV-malformed-readable"]["passed"] is True
