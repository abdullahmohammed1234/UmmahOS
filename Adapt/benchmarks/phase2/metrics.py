"""Phase 2 metrics. Reuses Phase 1E Wilson helpers."""

from __future__ import annotations

from typing import Any

from benchmarks.phase1e.metrics import appropriateness_rate, binary_flag_rate, evidence_sensitivity_rate
from benchmarks.phase1e.statistics import rate_payload


def _mean(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def compute_metrics(
    *,
    records: list[dict[str, Any]],
    counterfactuals: list[dict[str, Any]],
    recovery_records: list[dict[str, Any]] | None = None,
    cross_concept_records: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    recovery_records = recovery_records if recovery_records is not None else [
        item for item in records if item.get("recovery_scenario")
    ]
    cross_concept_records = cross_concept_records if cross_concept_records is not None else records
    separation = [item for item in records if item.get("separated") is not None]
    stability = [item for item in records if item.get("stability_scenario")]
    transitions = [item for item in records if item.get("strategy_path")]
    unnecessary = sum(1 for item in transitions if item.get("unnecessary_transition"))
    latencies = [
        float(item["recovery_latency"])
        for item in recovery_records
        if item.get("recovery_latency") is not None
    ]
    concepts = sorted({item.get("concept") for item in cross_concept_records if item.get("concept")})
    by_concept = {}
    for concept in concepts:
        subset = [item for item in cross_concept_records if item.get("concept") == concept]
        by_concept[concept] = appropriateness_rate(subset)

    return {
        "M2-001_strategy_appropriateness": appropriateness_rate(records),
        "M2-002_strategy_recovery": binary_flag_rate(recovery_records, "recovered_strategy")
        if recovery_records
        else rate_payload(0, 0),
        "M2-003_misconception_regression_separation": binary_flag_rate(separation, "separated")
        if separation
        else rate_payload(0, 0),
        "M2-004_strategy_stability": {
            **rate_payload(unnecessary, len(transitions) if transitions else 0),
            "note": "unnecessary transitions / scored trajectories; lower is better",
        },
        "M2-005_evidence_sensitivity": evidence_sensitivity_rate(counterfactuals)
        if counterfactuals
        else rate_payload(0, 0),
        "M2-006_strategy_traceability": binary_flag_rate(records, "traceable"),
        "M2-007_cross_concept_generalization": appropriateness_rate(cross_concept_records),
        "M2-007_by_concept": by_concept,
        "M2-008_recovery_latency": {
            "mean": None if _mean(latencies) is None else round(_mean(latencies), 3),
            "n": len(latencies),
            "values": latencies,
            "note": "successful evidence events before leaving REMEDIATE; not minimized by construction",
        },
        "counterfactual": {
            "differentiated": binary_flag_rate(counterfactuals, "differentiated")
            if counterfactuals
            else rate_payload(0, 0),
            "evidence_sensitive": evidence_sensitivity_rate(counterfactuals)
            if counterfactuals
            else rate_payload(0, 0),
        },
        "counts": {
            "scenarios": len(records),
            "recovery": len(recovery_records),
            "counterfactuals": len(counterfactuals),
            "concepts": concepts,
        },
    }
