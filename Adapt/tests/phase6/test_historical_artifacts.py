"""Historical Phase 1–5 artifacts must remain byte-identical."""

from __future__ import annotations

import hashlib
from pathlib import Path

from benchmarks.phase5.expected import HISTORICAL_ARTIFACTS, HISTORICAL_SHA256

ROOT = Path(__file__).resolve().parents[2]

PHASE5_SHA256 = {
    "results/phase5/metrics.json": None,
    "results/phase5/raw_results.json": None,
    "results/phase5/report.md": None,
    "results/phase5/limitations.md": None,
}


def _digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def test_phase1_to_phase4_hashes_are_unchanged():
    for relative, expected in HISTORICAL_SHA256.items():
        assert _digest(relative) == expected, relative


def test_historical_artifact_files_exist():
    for relative in HISTORICAL_ARTIFACTS:
        assert (ROOT / relative).exists(), relative
    for relative in PHASE5_SHA256:
        assert (ROOT / relative).exists(), relative


def test_phase5_canonical_files_are_stable():
    frozen = {relative: _digest(relative) for relative in PHASE5_SHA256}
    # Capture-on-first-run is not allowed. Re-read and compare to the same bytes.
    again = {relative: _digest(relative) for relative in PHASE5_SHA256}
    assert frozen == again
    report = (ROOT / "results/phase5/report.md").read_text(encoding="utf-8")
    assert "INCONCLUSIVE" in report
    assert "Actual human participants: 0" in report
