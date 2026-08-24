"""Phase 12 must not modify frozen engines or historical artifacts."""

from __future__ import annotations

import hashlib
from pathlib import Path

from benchmarks.phase5.expected import HISTORICAL_SHA256

ROOT = Path(__file__).resolve().parents[2]

ENGINE_FILES = (
    "src/adapt/analysis/evidence_analyzer.py",
    "src/adapt/state/state_updater.py",
    "src/adapt/strategy/engine.py",
    "src/adapt/adaptation/adaptation_engine.py",
    "src/adapt/tutor/tutor.py",
)


def test_frozen_engine_modules_do_not_import_llm():
    for relative in ENGINE_FILES:
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "adapt.llm" not in text
        assert "Gemini" not in text
        assert "GEMINI_API_KEY" not in text


def test_historical_phase_artifacts_were_not_rewritten():
    for relative, expected in HISTORICAL_SHA256.items():
        digest = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        assert digest == expected, relative


def test_phase5_still_inconclusive_in_docs():
    report = (ROOT / "docs" / "phase-5" / "5.md").read_text(encoding="utf-8")
    assert "INCONCLUSIVE" in report
    assert "n = 0" in report or "n=0" in report
