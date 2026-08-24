"""Phase 4 must not change Phase 3 engine decisions."""

from __future__ import annotations

from pathlib import Path

from tests.phase4.helpers import run_kinds_through_product, run_kinds_through_tutor

ROOT = Path(__file__).resolve().parents[2]


def test_product_preserves_phase3_decisions_for_shared_sequences():
    sequences = [
        ("strong_correct",) * 4,
        ("weak_correct",) * 4,
        ("strong_correct", "strong_correct", "misconception"),
        ("moderate_correct", "strong_correct", "weak_correct"),
    ]
    for kinds in sequences:
        _, _, product_results = run_kinds_through_product(kinds, session_id=f"REG-P-{len(kinds)}")
        _, _, tutor_traces = run_kinds_through_tutor(kinds, session_id=f"REG-T-{len(kinds)}")
        assert [item["result"]["adaptation"]["decision"] for item in product_results] == [
            item.decision.value for item in tutor_traces
        ]
        assert [item["research"]["next_challenge"]["challenge_id"] for item in product_results] == [
            item.next_challenge_id for item in tutor_traces
        ]


def test_historical_phase_artifacts_were_not_rewritten_by_phase4_source():
    # Presence check: Phase 4 must not delete historical result files.
    for relative in (
        "results/phase1e/metrics.json",
        "results/phase1f/metrics.json",
        "results/phase2/metrics.json",
        "results/phase3/metrics.json",
    ):
        assert (ROOT / relative).exists(), relative
