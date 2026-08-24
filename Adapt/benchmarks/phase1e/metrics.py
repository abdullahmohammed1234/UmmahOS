"""Phase 1E metric calculations. Pure functions over already-scored records."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from benchmarks.phase1e.statistics import percentage_point_difference, rate_payload, relative_improvement, mcnemar_test


def _safe_get(record: dict[str, Any], *keys: str, default: Any = None) -> Any:
    current: Any = record
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def appropriateness_rate(records: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(records)
    k = sum(1 for item in records if item.get("appropriate") is True)
    return rate_payload(k, n)


def counterfactual_differentiation_rate(pairs: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(pairs)
    k = sum(1 for item in pairs if item.get("differentiated") is True)
    return rate_payload(k, n)


def evidence_sensitivity_rate(pairs: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(pairs)
    k = sum(1 for item in pairs if item.get("evidence_sensitive") is True)
    return rate_payload(k, n)


def filtered_rate(records: list[dict[str, Any]], family: str | tuple[str, ...]) -> dict[str, Any]:
    families = {family} if isinstance(family, str) else set(family)
    subset = [item for item in records if item.get("family") in families]
    return appropriateness_rate(subset)


def binary_flag_rate(records: list[dict[str, Any]], field: str) -> dict[str, Any]:
    n = len(records)
    k = sum(1 for item in records if item.get(field) is True)
    return rate_payload(k, n)


def compare_systems(adapt: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    adapt_rate = adapt.get("rate")
    baseline_rate = baseline.get("rate")
    return {
        "adapt": adapt,
        "baseline": baseline,
        "percentage_point_difference": percentage_point_difference(adapt_rate, baseline_rate),
        "relative_improvement": relative_improvement(adapt_rate, baseline_rate),
    }


def paired_mcnemar(paired: list[dict[str, Any]]) -> dict[str, Any]:
    n10 = 0
    n01 = 0
    n11 = 0
    n00 = 0
    for item in paired:
        a = _safe_get(item, "adapt", "appropriate") is True
        b = _safe_get(item, "baseline", "appropriate") is True
        if a and not b:
            n10 += 1
        elif b and not a:
            n01 += 1
        elif a and b:
            n11 += 1
        else:
            n00 += 1
    result = mcnemar_test(n10, n01)
    result["n11"] = n11
    result["n00"] = n00
    return result


def family_breakdown(records: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in records:
        groups[str(item.get("family", "UNKNOWN"))].append(item)
    return {family: appropriateness_rate(items) for family, items in sorted(groups.items())}


def compute_metrics(
    *,
    adapt_records: list[dict[str, Any]],
    baseline_records: list[dict[str, Any]],
    paired: list[dict[str, Any]],
    adapt_pairs: list[dict[str, Any]],
    baseline_pairs: list[dict[str, Any]],
) -> dict[str, Any]:
    adapt_misc = [item for item in adapt_records if item.get("family") == "S-005"]
    base_misc = [item for item in baseline_records if item.get("family") == "S-005"]
    adapt_unc = [item for item in adapt_records if item.get("family") in {"S-002", "S-006", "S-007"}]
    base_unc = [item for item in baseline_records if item.get("family") in {"S-002", "S-006", "S-007"}]
    adapt_noise = [item for item in adapt_records if item.get("family") == "S-008"]
    base_noise = [item for item in baseline_records if item.get("family") == "S-008"]

    primary = {
        "M-001_decision_appropriateness": compare_systems(
            appropriateness_rate(adapt_records),
            appropriateness_rate(baseline_records),
        ),
        "M-002_counterfactual_differentiation": compare_systems(
            counterfactual_differentiation_rate(adapt_pairs),
            counterfactual_differentiation_rate(baseline_pairs),
        ),
        "M-003_evidence_sensitivity": compare_systems(
            evidence_sensitivity_rate(adapt_pairs),
            evidence_sensitivity_rate(baseline_pairs),
        ),
        "M-004_misconception_response": compare_systems(
            appropriateness_rate(adapt_misc),
            appropriateness_rate(base_misc),
        ),
        "M-005_uncertainty_handling": compare_systems(
            appropriateness_rate(adapt_unc),
            appropriateness_rate(base_unc),
        ),
        "M-006_noise_stability": compare_systems(
            binary_flag_rate(adapt_noise, "noise_stable"),
            binary_flag_rate(base_noise, "noise_stable"),
        ),
        "M-007_difficulty_appropriateness": compare_systems(
            binary_flag_rate(adapt_records, "difficulty_appropriate"),
            binary_flag_rate(baseline_records, "difficulty_appropriate"),
        ),
        "M-008_decision_traceability": compare_systems(
            binary_flag_rate(adapt_records, "traceable"),
            binary_flag_rate(baseline_records, "traceable"),
        ),
    }

    secondary = {
        "false_mastery_rate": compare_systems(
            binary_flag_rate(adapt_records, "false_mastery"),
            binary_flag_rate(baseline_records, "false_mastery"),
        ),
        "false_weakness_rate": compare_systems(
            binary_flag_rate(adapt_records, "false_weakness"),
            binary_flag_rate(baseline_records, "false_weakness"),
        ),
        "overreaction_rate": compare_systems(
            binary_flag_rate(adapt_records, "overreaction"),
            binary_flag_rate(baseline_records, "overreaction"),
        ),
        "underreaction_rate": compare_systems(
            binary_flag_rate(adapt_records, "underreaction"),
            binary_flag_rate(baseline_records, "underreaction"),
        ),
        "uncertainty_overconfidence_rate": compare_systems(
            binary_flag_rate(adapt_records, "uncertainty_overconfidence"),
            binary_flag_rate(baseline_records, "uncertainty_overconfidence"),
        ),
        "misconception_persistence_rate": compare_systems(
            binary_flag_rate(adapt_misc, "misconception_persisted"),
            binary_flag_rate(base_misc, "misconception_persisted"),
        ),
    }

    return {
        "primary": primary,
        "secondary": secondary,
        "adapt_by_family": family_breakdown(adapt_records),
        "baseline_by_family": family_breakdown(baseline_records),
        "paired_mcnemar_appropriateness": paired_mcnemar(paired),
        "counts": {
            "adapt_records": len(adapt_records),
            "baseline_records": len(baseline_records),
            "paired": len(paired),
            "counterfactual_pairs_adapt": len(adapt_pairs),
            "counterfactual_pairs_baseline": len(baseline_pairs),
        },
    }
