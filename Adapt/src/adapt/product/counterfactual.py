"""Counterfactual demonstration: same start, different evidence, actual engine."""

from __future__ import annotations

from typing import Any

DEFAULT_COUNTERFACTUAL = {
    "id": "phase4-cf-quality",
    "title": "Same challenge, different evidence",
    "challenge_id": "ALG-M-001",
    "concept_id": "basic_algebra",
    "topic_id": "algebra",
    "learner_a": {
        "label": "Learner A",
        "summary": "Correct · Strong reasoning · High confidence",
        "kinds": ["strong_correct", "strong_correct", "strong_correct"],
    },
    "learner_b": {
        "label": "Learner B",
        "summary": "Correct · Weak reasoning · Low confidence",
        "kinds": ["weak_correct", "weak_correct", "weak_correct"],
    },
}


def default_counterfactual() -> dict[str, Any]:
    return dict(DEFAULT_COUNTERFACTUAL)
