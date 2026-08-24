"""Phase 1F metrics. Reuses Phase 1E Wilson/rate helpers; does not redefine them."""

from __future__ import annotations

from typing import Any

from benchmarks.phase1e.metrics import appropriateness_rate, binary_flag_rate
from benchmarks.phase1e.statistics import rate_payload


def _rate(records: list[dict[str, Any]], predicate) -> dict[str, Any]:
    subset = [item for item in records if predicate(item)]
    return appropriateness_rate(subset) if subset else rate_payload(0, 0)


def development_holdout_gap(dev: dict[str, Any], holdout: dict[str, Any]) -> float | None:
    if dev.get("rate") is None or holdout.get("rate") is None:
        return None
    return dev["rate"] - holdout["rate"]


def assign_band(holdout_rate: float | None, gap: float | None, extras: dict[str, Any]) -> str:
    """Frozen interpretation bands from constants. Not tuned after seeing results."""
    if holdout_rate is None:
        return "NOT_ROBUST"
    metamorphic = extras.get("metamorphic_rate")
    adversarial_ok = extras.get("adversarial_no_override", False)
    recovery = extras.get("recovery_rate")
    if (
        holdout_rate >= 0.80
        and (gap is None or gap <= 0.10)
        and (metamorphic is None or metamorphic >= 0.80)
        and adversarial_ok
        and (recovery is None or recovery >= 0.70)
    ):
        return "ROBUST"
    if holdout_rate < 0.50:
        return "NOT_ROBUST"
    if holdout_rate >= 0.65 and (gap is None or gap <= 0.20):
        return "PARTIALLY_ROBUST"
    if holdout_rate >= 0.50:
        return "PARTIALLY_ROBUST"
    return "NOT_ROBUST"


def compute_metrics(
    *,
    development: list[dict[str, Any]],
    holdout: list[dict[str, Any]],
    all_records: list[dict[str, Any]],
    metamorphic: list[dict[str, Any]],
    adversarial: list[dict[str, Any]],
    longitudinal: list[dict[str, Any]],
) -> dict[str, Any]:
    recov = [item for item in all_records if item.get("recovery_scenario")]
    persist = [item for item in all_records if item.get("persistence_scenario")]
    unc = [item for item in all_records if item.get("family") in {"G-007", "G-008", "G-009", "G-012", "G-014"}]
    misc = [item for item in all_records if item.get("family") in {"G-003", "G-006", "G-011"}]
    noise = [item for item in all_records if item.get("family") == "G-004"]
    novel = [item for item in all_records if item.get("novel")]
    multi = [item for item in all_records if item.get("multi_dimension")]

    dev_app = appropriateness_rate(development)
    hold_app = appropriateness_rate(holdout)
    gap = development_holdout_gap(dev_app, hold_app)
    meta_rate = binary_flag_rate(metamorphic, "passed") if metamorphic else rate_payload(0, 0)
    adv_rate = binary_flag_rate(adversarial, "passed") if adversarial else rate_payload(0, 0)
    rec_rate = binary_flag_rate(recov, "recovered") if recov else rate_payload(0, 0)
    persist_rate = binary_flag_rate(persist, "misconception_persisted") if persist else rate_payload(0, 0)
    long_ok = binary_flag_rate(longitudinal, "stable") if longitudinal else rate_payload(0, 0)

    extras = {
        "metamorphic_rate": meta_rate.get("rate"),
        "adversarial_no_override": (adv_rate.get("rate") or 0) >= 1.0 if adversarial else False,
        "recovery_rate": rec_rate.get("rate"),
    }
    band = assign_band(hold_app.get("rate"), gap, extras)

    return {
        "M-001_decision_appropriateness": appropriateness_rate(all_records),
        "M-001_development": dev_app,
        "M-001_holdout": hold_app,
        "M-002_evidence_sensitivity": appropriateness_rate(
            [item for item in all_records if item.get("family") in {"G-007", "G-008", "G-009", "G-010", "G-012"}]
        ),
        "M-003_uncertainty_handling": appropriateness_rate(unc),
        "M-004_misconception_response": appropriateness_rate(misc),
        "M-005_noise_stability": appropriateness_rate(noise),
        "M-006_recovery": rec_rate,
        "M-007_state_stability": long_ok,
        "M-008_decision_traceability": binary_flag_rate(all_records, "traceable"),
        "M-009_generalization_rate": hold_app,
        "M-010_development_holdout_gap": gap,
        "M-011_state_recovery_rate": rec_rate,
        "M-012_misconception_persistence_rate": persist_rate,
        "M-013_overreaction_rate": rate_payload(
            sum(1 for item in all_records if item.get("failure_type") in {"OVERREACTION", "STABILITY_FAILURE"}),
            len(all_records) or 0,
        ),
        "M-014_underreaction_rate": rate_payload(
            sum(1 for item in all_records if (not item.get("appropriate")) and item.get("family") in {"G-001", "G-003", "G-006"}),
            len(all_records) or 0,
        ),
        "M-015_state_coherence": long_ok,
        "novel_appropriateness": appropriateness_rate(novel),
        "multi_dimension_appropriateness": appropriateness_rate(multi),
        "metamorphic": meta_rate,
        "adversarial": adv_rate,
        "counts": {
            "development": len(development),
            "holdout": len(holdout),
            "all": len(all_records),
            "metamorphic": len(metamorphic),
            "adversarial": len(adversarial),
            "longitudinal": len(longitudinal),
            "novel": len(novel),
            "multi_dimension": len(multi),
        },
        "outcome_band": band,
    }
