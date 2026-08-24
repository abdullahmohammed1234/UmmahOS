"""Phase 5 metrics M5-001 through M5-010."""

from __future__ import annotations

from typing import Any

from adapt.eval.statistics import analyze_records, mean


def compute_metrics(records: list[dict[str, Any]], *, label: str) -> dict[str, Any]:
    analysis = analyze_records(records)
    n = analysis["n"]
    survey_adapt = analysis["survey_adapt"]
    survey_base = analysis["survey_baseline"]
    return {
        "label": label,
        "n": n,
        "M5-001_learning_gain": {
            "adapt": analysis["gain_adapt"],
            "baseline": analysis["gain_baseline"],
            "delta": analysis["delta"],
        },
        "M5-002_misconception_recovery": {
            "adapt": analysis["misconception_recovery_adapt"],
            "baseline": analysis["misconception_recovery_baseline"],
        },
        "M5-003_post_test_accuracy": {
            "adapt": analysis["post_test_adapt"],
            "baseline": analysis["post_test_baseline"],
        },
        "M5-004_delayed_retention": {
            "status": "NOT COLLECTED",
            "adapt": None,
            "baseline": None,
        },
        "M5-005_perceived_adaptiveness": {
            "adapt": survey_adapt["perceived_adaptiveness"],
            "baseline": survey_base["perceived_adaptiveness"],
        },
        "M5-006_challenge_appropriateness": {
            "adapt": survey_adapt["challenge_appropriateness"],
            "baseline": survey_base["challenge_appropriateness"],
        },
        "M5-007_explanation_clarity": {
            "adapt": survey_adapt["explanation_clarity"],
            "baseline": survey_base["explanation_clarity"],
        },
        "M5-008_strategy_transition_quality": {
            "adapt": survey_adapt["explanation_clarity"],
            "baseline": survey_base["explanation_clarity"],
            "note": "Operationalized as Q3 (understood why the next challenge was given).",
        },
        "M5-009_session_completion": {
            "adapt": analysis["session_completion_adapt"],
            "baseline": analysis["session_completion_baseline"],
            "n": n,
        },
        "M5-010_engagement_dropout": {
            "adapt": analysis["dropout_adapt"],
            "baseline": analysis["dropout_baseline"],
            "n": n,
        },
        "pre_test": analysis["pre_test"],
        "interpretation": analysis["interpretation"],
        "method": analysis["method"],
        "analysis": analysis,
    }


def comparison_table(metrics: dict[str, Any]) -> list[dict[str, Any]]:
    def cell(side: dict[str, Any] | None) -> float | None:
        if not side:
            return None
        if "mean" in side:
            return side.get("mean")
        return None

    gain = metrics["M5-001_learning_gain"]
    rec = metrics["M5-002_misconception_recovery"]
    post = metrics["M5-003_post_test_accuracy"]
    perc = metrics["M5-005_perceived_adaptiveness"]
    chal = metrics["M5-006_challenge_appropriateness"]
    pre = metrics["pre_test"]
    rows = [
        ("Pre-test", pre, pre),
        ("Post-test", post["adapt"], post["baseline"]),
        ("Learning gain", gain["adapt"], gain["baseline"]),
        ("Misconception recovery", rec["adapt"], rec["baseline"]),
        ("Perceived adaptiveness", perc["adapt"], perc["baseline"]),
        ("Challenge appropriateness", chal["adapt"], chal["baseline"]),
    ]
    table = []
    for name, adapt, baseline in rows:
        a = cell(adapt)
        b = cell(baseline)
        diff = None if a is None or b is None else a - b
        table.append({"metric": name, "adapt": a, "baseline": b, "difference": diff})
    _ = mean
    return table
