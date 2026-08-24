"""Phase 8 metrics computed from real execution."""

from __future__ import annotations

from typing import Any

TARGETS = {
    "M8-001": 1.0,
    "M8-002": 1.0,
    "M8-003": 1.0,
    "M8-004": 1.0,
    "M8-005": 1.0,
    "M8-006": 1.0,
    "M8-007": 1.0,
    "M8-008": 1.0,
    "M8-009": 1.0,
    "M8-010": 1.0,
    "M8-011": 1.0,
    "M8-012": 1.0,
}


def compute_metrics(payload: dict[str, Any]) -> dict[str, Any]:
    def row(metric_id: str, value: float, display: str, passed: bool) -> dict[str, Any]:
        return {
            "id": metric_id,
            "value": value,
            "target": TARGETS[metric_id],
            "display": display,
            "passed": passed,
        }

    nav = 1.0 if payload["navigation"]["ok"] else 0.0
    concepts = 1.0 if payload["concepts"]["ok"] else 0.0
    complete = payload["challenge"]["completed"] / payload["challenge"]["total"]
    lightweight = 1.0 if payload["lightweight"]["ok"] else 0.0
    coverage = payload["explanations"]["complete"] / payload["explanations"]["total"]
    consistent = 1.0 if payload["explanations"]["consistent"] else 0.0
    progress_ok = 1.0 if payload["progress"]["ok"] else 0.0
    repetition = payload["repetition"]["avoided"] / payload["repetition"]["eligible"] if payload["repetition"]["eligible"] else 1.0
    cf = 1.0 if payload["counterfactual"]["preserved"] else 0.0
    research = 1.0 if payload["research"]["ok"] else 0.0
    engine = 1.0 if payload["engine"]["preserved"] else 0.0
    det = 1.0 if payload["determinism"]["identical"] else 0.0

    metrics = {
        "M8-001_navigation": row("M8-001", nav, "complete" if nav else "missing", nav >= 1),
        "M8-002_concept_accessibility": row("M8-002", concepts, "reachable" if concepts else "blocked", concepts >= 1),
        "M8-003_challenge_completion": row("M8-003", complete, f"{payload['challenge']['completed']}/{payload['challenge']['total']}", complete >= 1),
        "M8-004_lightweight_evidence": row("M8-004", lightweight, "optional reasoning" if lightweight else "forced essay", lightweight >= 1),
        "M8-005_explanation_coverage": row("M8-005", coverage, f"{payload['explanations']['complete']}/{payload['explanations']['total']}", coverage >= 1),
        "M8-006_trace_consistency": row("M8-006", consistent, "consistent" if consistent else "diverged", consistent >= 1),
        "M8-007_progress_correctness": row("M8-007", progress_ok, "honest" if progress_ok else "fabricated", progress_ok >= 1),
        "M8-008_repetition_avoidance": row("M8-008", repetition, f"{repetition:.1%}", repetition >= 1),
        "M8-009_counterfactual": row("M8-009", cf, "preserved" if cf else "lost", cf >= 1),
        "M8-010_research_trace": row("M8-010", research, "visible" if research else "missing", research >= 1),
        "M8-011_engine_preservation": row("M8-011", engine, "preserved" if engine else "changed", engine >= 1),
        "M8-012_determinism": row("M8-012", det, "identical" if det else "diverged", det >= 1),
    }
    failures = [item["id"] for item in metrics.values() if not item["passed"]]
    return {"metrics": metrics, "failures": failures, "passed": not failures}
