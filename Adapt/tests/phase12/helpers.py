from __future__ import annotations

import json

VALID_EVIDENCE = {
    "correctness": "correct",
    "reasoning_quality": "weak",
    "confidence_signal": "low",
    "misconception": None,
    "error_type": None,
    "evidence_strength": "weak",
    "uncertainty": "high",
    "supporting_evidence": ["I guessed"],
}

STRONG_EVIDENCE = {
    "correctness": "correct",
    "reasoning_quality": "strong",
    "confidence_signal": "high",
    "misconception": None,
    "error_type": None,
    "evidence_strength": "strong",
    "uncertainty": "low",
    "supporting_evidence": ["divided both sides"],
}


def dumps(payload: dict) -> str:
    return json.dumps(payload)
