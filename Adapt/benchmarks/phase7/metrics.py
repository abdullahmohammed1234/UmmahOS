"""Phase 7 metrics."""

from __future__ import annotations

from typing import Any

from benchmarks.phase7.expected import TARGETS


def compute_metrics(payload: dict[str, Any]) -> dict[str, Any]:
    catalog = payload["catalog"]
    repetition = payload["repetition"]
    consistency = payload["consistency"]
    traces = payload["traces"]
    counterfactual = payload["counterfactual"]
    determinism = payload["determinism"]

    m1 = catalog["subjects"]
    m2 = catalog["concepts"]
    m3 = catalog["challenge_types"]
    m4 = repetition["avoided"] / repetition["eligible"] if repetition["eligible"] else 1.0
    m5 = consistency["ok"] / consistency["total"] if consistency["total"] else 1.0
    m6 = traces["complete"] / traces["total"] if traces["total"] else 1.0
    m7 = 1.0 if counterfactual["preserved"] else 0.0
    m8 = 1.0 if determinism["identical"] else 0.0

    def row(metric_id: str, value: float, target, display: str, passed: bool) -> dict[str, Any]:
        return {
            "id": metric_id,
            "value": value,
            "target": target,
            "display": display,
            "passed": passed,
        }

    metrics = {
        "M7-001_subject_coverage": row("M7-001", m1, TARGETS["M7-001"], f"{m1} domains", m1 >= TARGETS["M7-001"]),
        "M7-002_concept_coverage": row("M7-002", m2, TARGETS["M7-002"], f"{m2} concepts", m2 >= TARGETS["M7-002"]),
        "M7-003_challenge_diversity": row("M7-003", m3, TARGETS["M7-003"], f"{m3} types", m3 >= TARGETS["M7-003"]),
        "M7-004_repetition_avoidance": row("M7-004", m4, TARGETS["M7-004"], f"{m4:.1%}", m4 >= TARGETS["M7-004"]),
        "M7-005_strategy_to_challenge": row("M7-005", m5, TARGETS["M7-005"], f"{consistency['ok']}/{consistency['total']}", m5 >= TARGETS["M7-005"]),
        "M7-006_trace_completeness": row("M7-006", m6, TARGETS["M7-006"], f"{traces['complete']}/{traces['total']}", m6 >= TARGETS["M7-006"]),
        "M7-007_counterfactual": row("M7-007", m7, TARGETS["M7-007"], "preserved" if m7 == 1 else "lost", m7 >= TARGETS["M7-007"]),
        "M7-008_determinism": row("M7-008", m8, TARGETS["M7-008"], "identical" if m8 == 1 else "diverged", m8 >= TARGETS["M7-008"]),
    }
    failures = [item["id"] for item in metrics.values() if not item["passed"]]
    return {"metrics": metrics, "failures": failures, "passed": not failures}
