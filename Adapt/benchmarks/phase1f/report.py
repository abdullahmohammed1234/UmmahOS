"""Phase 1F human-readable report."""

from __future__ import annotations

from typing import Any


def _pct(block: dict[str, Any] | None) -> str:
    if not block:
        return "n/a"
    return str(block.get("display") or "n/a")


def _find(records: list[dict[str, Any]], family: str, ok: bool | None = True) -> dict[str, Any] | None:
    for item in records:
        if item.get("family") != family:
            continue
        if ok is None or item.get("appropriate") is ok:
            return item
    return None


def render_report(
    *,
    meta: dict[str, Any],
    metrics: dict[str, Any],
    development: list[dict[str, Any]],
    holdout: list[dict[str, Any]],
    all_records: list[dict[str, Any]],
    metamorphic: list[dict[str, Any]],
    adversarial: list[dict[str, Any]],
    longitudinal: list[dict[str, Any]],
) -> str:
    failures = [item for item in all_records if item.get("appropriate") is False]
    hold_fail = [item for item in holdout if item.get("appropriate") is False]
    band = metrics.get("outcome_band")
    gap = metrics.get("M-010_development_holdout_gap")
    gap_s = "n/a" if gap is None else f"{gap * 100:+.1f} pp"
    rec_ok = _find(all_records, "G-005", True)
    conf_ok = _find(all_records, "G-007", True)
    gen_ok = _find(all_records, "G-001", True)
    worst = None
    for item in failures:
        if item.get("severity") == "HIGH":
            worst = item
            break
    if worst is None and failures:
        worst = failures[0]
    lines = [
        "# ADAPT Phase 1F Report",
        "",
        "## Executive summary",
        "",
        f"Outcome band: **{band}**",
        "",
        f"Development appropriateness: {_pct(metrics['M-001_development'])}",
        f"Holdout appropriateness: {_pct(metrics['M-001_holdout'])}",
        f"Generalization gap (dev − holdout): {gap_s}",
        "",
        "## Hypothesis",
        "",
        "H1: ADAPT's evidence-driven adaptation generalizes to unseen learner scenarios without becoming unstable or overconfident.",
        "",
        "## Benchmark methodology",
        "",
        "Phase 1E is unchanged. Phase 1F uses novel families, a fractions concept bank that does not alter Phase 1D/1E items, a frozen holdout ID set, metamorphic relations, adversarial inputs, and 20-step trajectories.",
        "",
        "## Scenario distribution",
        "",
        f"- Scored scenarios: {metrics['counts']['all']}",
        f"- Development: {metrics['counts']['development']}",
        f"- Holdout: {metrics['counts']['holdout']}",
        f"- Novel: {metrics['counts']['novel']}",
        f"- Multi-dimension: {metrics['counts']['multi_dimension']}",
        f"- Longitudinal trajectories: {metrics['counts']['longitudinal']}",
        "",
        "## Development results",
        "",
        _pct(metrics["M-001_development"]),
        "",
        "## Holdout results",
        "",
        _pct(metrics["M-001_holdout"]),
        "",
        "## Generalization gap",
        "",
        gap_s,
        "",
        "## Primary / Phase 1F metrics",
        "",
        f"- M-001 all: {_pct(metrics['M-001_decision_appropriateness'])}",
        f"- M-002 evidence sensitivity: {_pct(metrics['M-002_evidence_sensitivity'])}",
        f"- M-003 uncertainty: {_pct(metrics['M-003_uncertainty_handling'])}",
        f"- M-004 misconception: {_pct(metrics['M-004_misconception_response'])}",
        f"- M-005 noise: {_pct(metrics['M-005_noise_stability'])}",
        f"- M-006/M-011 recovery: {_pct(metrics['M-006_recovery'])}",
        f"- M-007/M-015 stability: {_pct(metrics['M-007_state_stability'])}",
        f"- M-008 traceability: {_pct(metrics['M-008_decision_traceability'])}",
        f"- M-009 holdout generalization: {_pct(metrics['M-009_generalization_rate'])}",
        f"- M-012 misconception persistence (recovery leftovers): {_pct(metrics['M-012_misconception_persistence_rate'])}",
        "",
        "## Metamorphic results",
        "",
    ]
    for item in metamorphic:
        lines.append(f"- {item['test_id']}: {'PASS' if item['passed'] else 'FAIL'} ({item['note']})")
    lines.extend(["", "## Adversarial results", ""])
    for item in adversarial:
        lines.append(f"- {item['test_id']}: {'PASS' if item['passed'] else 'FAIL'} decision={item.get('decision')}")
    lines.extend(["", "## Longitudinal results", ""])
    for item in longitudinal:
        lines.append(
            f"- {item['trajectory_id']} steps={item['steps']} stable={item['stable']} "
            f"final={item['final_decision']} mastery={item['final_mastery']:.3f}"
        )
    lines.extend(
        [
            "",
            "## State recovery results",
            "",
            _pct(metrics["M-011_state_recovery_rate"]),
            "",
            "## Misconception results",
            "",
            _pct(metrics["M-004_misconception_response"]),
            "",
            "## Failure analysis",
            "",
            f"Scored-scenario failures: {len(failures)} (holdout {len(hold_fail)})",
            "",
        ]
    )
    for item in failures:
        lines.append(
            f"- `{item['scenario_id']}` split={item['split']} decision=`{item['decision']}` "
            f"type={item.get('failure_type')} severity={item.get('severity')}"
        )
    lines.extend(["", "## Representative successes", ""])
    if gen_ok:
        lines.append(f"- Concept transfer: `{gen_ok['scenario_id']}` → {gen_ok['decision']}")
    if rec_ok:
        lines.append(f"- Recovery: `{rec_ok['scenario_id']}` → {rec_ok['decision']} recovered={rec_ok.get('recovered')}")
    if conf_ok:
        lines.append(f"- Confidence/evidence conflict: `{conf_ok['scenario_id']}` → {conf_ok['decision']}")
    meta_ok = next((item for item in metamorphic if item["passed"]), None)
    adv_ok = next((item for item in adversarial if item["passed"]), None)
    long_ok = next((item for item in longitudinal if item.get("stable")), None)
    if meta_ok:
        lines.append(f"- Metamorphic: {meta_ok['test_id']}")
    if adv_ok:
        lines.append(f"- Adversarial: {adv_ok['test_id']}")
    if long_ok:
        lines.append(f"- Longitudinal: {long_ok['trajectory_id']} ({long_ok['steps']} steps)")
    lines.extend(["", "## Worst failure", ""])
    if worst:
        lines.append(
            f"`{worst['scenario_id']}` ({worst['split']}) decision={worst['decision']} "
            f"expected={worst['expected_decisions']} type={worst.get('failure_type')}"
        )
        lines.append(str(worst.get("expected_behavior")))
    else:
        lines.append("No scored-scenario failures.")
    lines.extend(
        [
            "",
            "## Limitations",
            "",
            "- Deterministic keyword analysis, not an LLM.",
            "- Fractions bank lives in Phase 1F only; Phase 1D/1E algebra items were not edited.",
            "- Correct-answer + wrong-explanation cannot raise misconception_signal in the Phase 1D analyzer.",
            "- Family-level samples are small; Wilson intervals are wide.",
            "",
            "## Reproducibility information",
            "",
            f"- Version: {meta.get('benchmark_version')}",
            f"- Seed: {meta.get('random_seed')}",
            f"- Timestamp: {meta.get('timestamp')}",
            f"- Python: {meta.get('python_version')}",
            f"- Git: {meta.get('git_commit')}",
            f"- Holdout IDs frozen: {meta.get('holdout_count')}",
            "",
            "## Conclusion",
            "",
            f"{band}. See docs/phase-1/1F.md for interpretation against the pre-registered bands.",
            "",
        ]
    )
    return "\n".join(lines)
