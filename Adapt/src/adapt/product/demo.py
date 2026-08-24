"""Guided 2–3 minute demo. Predefined responses; actual AdaptiveTutor decisions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
DEMO_SCENARIO_PATH = ROOT / "demo" / "scenario.json"

# Frozen after probing AdaptiveTutor(seed=20260814) on ALG-D-001.
# The kinds are inputs. Strategies and next challenges are NOT hardcoded.
DEFAULT_DEMO = {
    "id": "phase4-guided-demo",
    "title": "ADAPT guided demo",
    "topic_id": "algebra",
    "concept_id": "basic_algebra",
    "initial_challenge": "ALG-D-001",
    "max_steps": 9,
    "beats": [
        "Initial assessment",
        "Strong evidence",
        "Increased difficulty",
        "Uncertainty",
        "Probe",
        "Misconception",
        "Remediation",
        "Recovery",
        "Progress again",
    ],
    "responses": [
        {"kind": "strong_correct"},
        {"kind": "strong_correct"},
        {"kind": "strong_correct"},
        {"kind": "weak_correct"},
        {"kind": "misconception"},
        {"kind": "misconception"},
        {"kind": "misconception"},
        {"kind": "strong_correct"},
        {"kind": "strong_correct"},
    ],
}


def load_demo_scenario() -> dict[str, Any]:
    if DEMO_SCENARIO_PATH.exists():
        import json

        return json.loads(DEMO_SCENARIO_PATH.read_text(encoding="utf-8"))
    return dict(DEFAULT_DEMO)
