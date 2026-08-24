"""Prompt-selection criteria for Phase 12. Frozen before holdout evaluation."""

from __future__ import annotations

from typing import Any

# Pre-registered scoring weights. Do not retune after inspecting holdout.
CRITERIA_WEIGHTS = {
    "structured_output_validity": 0.30,
    "evidence_extraction_accuracy": 0.30,
    "prompt_injection_robustness": 0.20,
    "no_strategy_leakage": 0.10,
    "counterfactual_sensitivity": 0.10,
}

CRITERIA_VERSION = "phase12-criteria-v1"


def prompt_score(metrics: dict[str, float]) -> float:
    total = 0.0
    for key, weight in CRITERIA_WEIGHTS.items():
        total += weight * float(metrics.get(key) or 0.0)
    return total


def select_prompt(results_by_prompt: dict[str, dict[str, Any]]) -> dict[str, Any]:
    ranked = []
    for prompt_id, payload in results_by_prompt.items():
        score = prompt_score(payload.get("criteria") or payload)
        ranked.append((score, prompt_id, payload))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    winner_score, winner_id, winner_payload = ranked[0]
    return {
        "selected_prompt_id": winner_id,
        "score": winner_score,
        "criteria_version": CRITERIA_VERSION,
        "weights": dict(CRITERIA_WEIGHTS),
        "ranking": [
            {"prompt_id": prompt_id, "score": score} for score, prompt_id, _payload in ranked
        ],
        "rule": (
            "Select the development-set prompt with the highest weighted score. "
            "Holdout is evaluated once after selection."
        ),
    }
