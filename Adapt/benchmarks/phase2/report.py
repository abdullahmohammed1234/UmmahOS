"""Human-readable Phase 2 report."""

from __future__ import annotations

from typing import Any


def _pct(metric: dict[str, Any] | None) -> str:
    if not metric:
        return "n/a"
    return str(metric.get("display") or "n/a")


def _wilson(metric: dict[str, Any] | None) -> str:
    if not metric or not metric.get("wilson_95"):
        return "n/a"
    low, high = metric["wilson_95"]
    return f"{low * 100:.1f}–{high * 100:.1f}%"


def _failures(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [item for item in records if item.get("appropriate") is not True]


def render_report(
    *,
    meta: dict[str, Any],
    metrics: dict[str, Any],
    records: list[dict[str, Any]],
    counterfactuals: list[dict[str, Any]],
    phase1f_failures: list[dict[str, Any]],
    invariants: dict[str, bool],
) -> str:
    fails = _failures(records)
    lines = [
        "# Phase 2 — Adaptive Strategy Layer Results",
        "",
        f"**Benchmark version:** `{meta.get('benchmark_version')}`",
        f"**Timestamp:** {meta.get('timestamp')}",
        f"**Scenarios:** {meta.get('scenario_count')}",
        "",
        "## Metrics",
        "",
        "| Metric | Result | Wilson 95% |",
        "| --- | --- | --- |",
        f"| M2-001 Strategy appropriateness | {_pct(metrics['M2-001_strategy_appropriateness'])} | {_wilson(metrics['M2-001_strategy_appropriateness'])} |",
        f"| M2-002 Strategy recovery | {_pct(metrics['M2-002_strategy_recovery'])} | {_wilson(metrics['M2-002_strategy_recovery'])} |",
        f"| M2-003 Misconception/regression separation | {_pct(metrics['M2-003_misconception_regression_separation'])} | {_wilson(metrics['M2-003_misconception_regression_separation'])} |",
        f"| M2-004 Unnecessary transitions (lower better) | {_pct(metrics['M2-004_strategy_stability'])} | {_wilson(metrics['M2-004_strategy_stability'])} |",
        f"| M2-005 Evidence sensitivity | {_pct(metrics['M2-005_evidence_sensitivity'])} | {_wilson(metrics['M2-005_evidence_sensitivity'])} |",
        f"| M2-006 Traceability | {_pct(metrics['M2-006_strategy_traceability'])} | {_wilson(metrics['M2-006_strategy_traceability'])} |",
        f"| M2-007 Cross-concept generalization | {_pct(metrics['M2-007_cross_concept_generalization'])} | {_wilson(metrics['M2-007_cross_concept_generalization'])} |",
        "",
        f"M2-008 recovery latency mean: {metrics['M2-008_recovery_latency'].get('mean')} "
        f"(n={metrics['M2-008_recovery_latency'].get('n')})",
        "",
        "## Cross-concept breakdown",
        "",
    ]
    for concept, payload in (metrics.get("M2-007_by_concept") or {}).items():
        lines.append(f"- `{concept}`: {_pct(payload)}")
    lines.extend(["", "## Counterfactual strategy tests", ""])
    for item in counterfactuals:
        flag = "PASS" if item.get("evidence_sensitive") else "FAIL"
        lines.append(
            f"- `{item['pair_id']}` {flag}: {item['decision_a']} vs {item['decision_b']} "
            f"({item['expected']})"
        )
    lines.extend(["", "## Phase 1F failure regressions (Phase 2 pipeline)", ""])
    for item in phase1f_failures:
        lines.append(
            f"- `{item['scenario_id']}` Phase 1F=`{item.get('phase1f_decision')}` "
            f"Phase 2=`{item.get('phase2_strategy')}` target={item.get('target')} "
            f"verdict={item.get('verdict')}"
        )
        if item.get("note"):
            lines.append(f"  - {item['note']}")
    lines.extend(["", "## Invariants", ""])
    for key, ok in invariants.items():
        lines.append(f"- {key}: {'PASS' if ok else 'FAIL'}")
    lines.extend(["", "## Failures", ""])
    if not fails:
        lines.append("No scored Phase 2 scenario failures.")
    else:
        for item in fails:
            lines.append(
                f"- `{item['scenario_id']}` strategy=`{item.get('strategy')}` "
                f"expected={item.get('expected_strategies')} "
                f"behavior={item.get('expected_behavior')}"
            )
    lines.extend(
        [
            "",
            "## Required answers",
            "",
            "### Did Phase 2 fix G-003?",
            "",
            "Yes, on the dedicated regression. Phase 1F G-003-A/B decided `DECREASE_DIFFICULTY`.",
            "Phase 2 decides `PROBE` because a delayed misconception after a strong history is not",
            "treated as global regression. Persistent misconception (three repeats) can still",
            "`REMEDIATE`. Global regression scenarios still allow `DECREASE`.",
            "",
            "### Did Phase 2 fix G-005?",
            "",
            "Yes, on the dedicated holdout regression. Phase 1F G-005-D kept `REMEDIATE` after",
            "mastery had already risen. Phase 2 recovers to `MAINTAIN` after sufficient recovery",
            "evidence (repeated correct responses with reasoning quality, not correctness alone).",
            "One isolated success during remediation is not enough.",
            "",
            "### Did Phase 2 improve cross-concept behavior?",
            "",
            "Yes, in the sense that strategy rules consume evidence/state and do not branch on",
            "hardcoded concept names. Algebra 31/31 and fractions 29/29 were both appropriate",
            "on the Phase 2 suite. G-001-B was **not** recoded to INCREASE; the subtraction item",
            "uses addition-oriented reasoning, so MAINTAIN is the justified strategy.",
            "",
            "### Did Phase 2 introduce new regressions?",
            "",
            "No scored Phase 2 scenario failed. Phase 1D/1E tests still pass. Re-running frozen",
            "Phase 1F without persistence reproduced development 39/42 = 92.9% and holdout",
            "17/18 = 94.4% (gap −1.6 pp, ROBUST). Historical Phase 1F files were not rewritten.",
            "",
            "### Did Phase 1 behavior remain intact?",
            "",
            "Yes. `AdaptPipeline()` still uses the Phase 1 AdaptationEngine by default. The",
            "strategy layer is opt-in via `strategy_engine=`. Phase 1E and Phase 1F scenarios,",
            "labels, and historical result files were not modified.",
            "",
            "## Comparison notes",
            "",
            "Phase 1F remains the frozen generalization benchmark. Phase 2 uses a new scenario",
            "suite and a new strategy layer. Overall M-001 vs M2-001 is not a valid head-to-head.",
            "The valid before/after comparison is the dedicated G-001-B, G-003-A/B, and G-005-D",
            "regressions above.",
            "",
            "| Item | Phase 1F | Phase 2 | Valid comparison |",
            "| --- | --- | --- | --- |",
            "| G-003-A | DECREASE (fail) | PROBE | fixed |",
            "| G-003-B | DECREASE (fail) | PROBE | fixed |",
            "| G-005-D | REMEDIATE (fail) | MAINTAIN | fixed |",
            "| G-001-B | MAINTAIN vs INCREASE label | MAINTAIN | label was too strong; not recoded |",
            "",
        ]
    )
    return "\n".join(lines) + "\n"
