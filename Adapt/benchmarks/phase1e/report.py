"""Generate the human-readable Phase 1E report from executed results."""

from __future__ import annotations

from typing import Any


def _pct(metric: dict[str, Any] | None) -> str:
    if not metric:
        return "n/a"
    display = metric.get("display")
    return str(display) if display else "n/a"


def _cmp(block: dict[str, Any]) -> str:
    adapt = block.get("adapt") or {}
    baseline = block.get("baseline") or {}
    diff = block.get("percentage_point_difference")
    rel = block.get("relative_improvement")
    diff_s = "n/a" if diff is None else f"{diff:+.1f} pp"
    rel_s = "n/a" if rel is None else f"{rel * 100:+.1f}%"
    return (
        f"- ADAPT: {_pct(adapt)}\n"
        f"- BASELINE: {_pct(baseline)}\n"
        f"- Difference: {diff_s}\n"
        f"- Relative improvement: {rel_s}"
    )


def _find(records: list[dict[str, Any]], family: str, system_ok: bool | None = None) -> dict[str, Any] | None:
    for item in records:
        if item.get("family") != family:
            continue
        if system_ok is None or item.get("appropriate") is system_ok:
            return item
    return None


def _example_block(title: str, paired_item: dict[str, Any] | None) -> str:
    if paired_item is None:
        return f"### {title}\n\nNo matching executed example was found.\n"
    adapt = paired_item["adapt"]
    baseline = paired_item["baseline"]
    return (
        f"### {title}\n\n"
        f"- Scenario: `{adapt['scenario_id']}`\n"
        f"- Expected: {adapt['expected_behavior']}\n"
        f"- ADAPT decision: `{adapt['decision']}` ({'appropriate' if adapt['appropriate'] else 'not appropriate'})\n"
        f"- Baseline decision: `{baseline['decision']}` ({'appropriate' if baseline['appropriate'] else 'not appropriate'})\n"
        f"- ADAPT evidence: `{adapt.get('evidence')}`\n"
        f"- Baseline diagnosis: {baseline.get('baseline_diagnosis')}\n"
    )


def _paired_by_id(paired: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {item["scenario_id"]: item for item in paired}


def _hypothesis_verdict(metrics: dict[str, Any]) -> tuple[str, str]:
    primary = metrics["primary"]
    adapt_app = primary["M-001_decision_appropriateness"]["adapt"].get("rate") or 0
    base_app = primary["M-001_decision_appropriateness"]["baseline"].get("rate") or 0
    adapt_cf = primary["M-002_counterfactual_differentiation"]["adapt"].get("rate") or 0
    base_cf = primary["M-002_counterfactual_differentiation"]["baseline"].get("rate") or 0
    adapt_misc = primary["M-004_misconception_response"]["adapt"].get("rate") or 0
    adapt_unc = primary["M-005_uncertainty_handling"]["adapt"].get("rate") or 0
    adapt_noise = primary["M-006_noise_stability"]["adapt"].get("rate") or 0
    adapt_trace = primary["M-008_decision_traceability"]["adapt"].get("rate") or 0
    advantage = (adapt_app - base_app) >= 0.05 or (adapt_cf - base_cf) >= 0.05
    strong = (
        adapt_cf >= 0.8
        and adapt_misc >= 0.8
        and adapt_unc >= 0.8
        and adapt_noise >= 0.8
        and adapt_trace >= 0.8
        and advantage
    )
    if strong:
        return "SUPPORTED", "ADAPT met the predefined strong-support pattern on this frozen benchmark."
    if advantage or adapt_trace > (primary["M-008_decision_traceability"]["baseline"].get("rate") or 0):
        return "PARTIALLY SUPPORTED", "Evidence is mixed. Some predefined criteria favor ADAPT; not all strong-support conditions were met."
    return "NOT SUPPORTED BY THIS BENCHMARK", "This benchmark did not demonstrate a meaningful ADAPT advantage on the frozen criteria."


def render_report(
    *,
    meta: dict[str, Any],
    metrics: dict[str, Any],
    paired: list[dict[str, Any]],
    adapt_pairs: list[dict[str, Any]],
    baseline_pairs: list[dict[str, Any]],
    adapt_records: list[dict[str, Any]],
    baseline_records: list[dict[str, Any]],
) -> str:
    verdict, verdict_text = _hypothesis_verdict(metrics)
    by_id = _paired_by_id(paired)
    mastery = _find(adapt_records, "S-001", True)
    lucky = _find(adapt_records, "S-002", True)
    misc = _find(adapt_records, "S-005", True)
    failure = next((item for item in adapt_records if item.get("appropriate") is False), None)
    cf_pair = next((item for item in paired if item["adapt"].get("counterfactual_pair_id")), None)
    failures = [item for item in adapt_records if item.get("appropriate") is False]
    base_failures = [item for item in baseline_records if item.get("appropriate") is False]
    mcnemar = metrics["paired_mcnemar_appropriateness"]
    lines = [
        "# ADAPT Phase 1E Benchmark Report",
        "",
        "## 1. Executive summary",
        "",
        f"Hypothesis evaluation: **{verdict}**",
        "",
        verdict_text,
        "",
        f"Scenario executions: {metrics['counts']['adapt_records']}",
        "",
        "## 2. Hypothesis",
        "",
        "H1: ADAPT will make more evidence-appropriate instructional decisions than the baseline because it explicitly represents learner evidence, learner state, uncertainty, and adaptation decisions.",
        "",
        "H0: ADAPT does not demonstrate a meaningful advantage over the baseline on the predefined evaluation criteria.",
        "",
        "## 3. Systems compared",
        "",
        "- BASELINE-001: simple deterministic heuristic tutor. Inspects response, reasoning, confidence, history, and challenge. Does not maintain ADAPT learner state.",
        "- ADAPT-001: Phase 1D pipeline (Evidence Analyzer → State Updater → Adaptation Engine → Challenge Selector).",
        "",
        "## 4. Benchmark methodology",
        "",
        "Both systems received the same scenario, current challenge, learner response, and history. Expected labels were not provided to either system. The benchmark is deterministic.",
        "",
        "## 5. Scenario suite",
        "",
        f"- Families: 12 required families plus two extra counterfactual pair families.",
        f"- Executions: {metrics['counts']['adapt_records']}",
        f"- Counterfactual pairs: {metrics['counts']['counterfactual_pairs_adapt']}",
        "",
        "## 6. Metrics",
        "",
        "### M-001 Decision appropriateness",
        _cmp(metrics["primary"]["M-001_decision_appropriateness"]),
        "",
        "### M-002 Counterfactual differentiation",
        _cmp(metrics["primary"]["M-002_counterfactual_differentiation"]),
        "",
        "### M-003 Evidence sensitivity",
        _cmp(metrics["primary"]["M-003_evidence_sensitivity"]),
        "",
        "### M-004 Misconception response",
        _cmp(metrics["primary"]["M-004_misconception_response"]),
        "",
        "### M-005 Uncertainty handling",
        _cmp(metrics["primary"]["M-005_uncertainty_handling"]),
        "",
        "### M-006 Noise stability",
        _cmp(metrics["primary"]["M-006_noise_stability"]),
        "",
        "### M-007 Difficulty appropriateness",
        _cmp(metrics["primary"]["M-007_difficulty_appropriateness"]),
        "",
        "### M-008 Decision traceability",
        _cmp(metrics["primary"]["M-008_decision_traceability"]),
        "",
        "## 7. Statistical methodology",
        "",
        "Binary rates use Wilson 95% confidence intervals. Paired appropriateness uses McNemar's test on discordant pairs. p-values are descriptive for this prototype sample.",
        "",
        f"McNemar n10 (ADAPT only appropriate) = {mcnemar['n10']}, n01 (baseline only appropriate) = {mcnemar['n01']}, statistic = {mcnemar['statistic']:.3f}, p = {mcnemar['p_value']:.4f}. {mcnemar.get('note', '')}",
        "",
        "## 8. ADAPT results",
        "",
        "\n".join(f"- {family}: {payload['display']}" for family, payload in metrics["adapt_by_family"].items()),
        "",
        "## 9. Baseline results",
        "",
        "\n".join(f"- {family}: {payload['display']}" for family, payload in metrics["baseline_by_family"].items()),
        "",
        "## 10. Paired comparison",
        "",
        _cmp(metrics["primary"]["M-001_decision_appropriateness"]),
        "",
        "## 11. Counterfactual results",
        "",
        "ADAPT pairs:",
    ]
    for item in adapt_pairs:
        lines.append(
            f"- {item['pair_id']} ({item['dimension']}): {item['decision_a']} vs {item['decision_b']} "
            f"differentiated={item['differentiated']} sensitive={item['evidence_sensitive']}"
        )
    lines.extend(["", "Baseline pairs:"])
    for item in baseline_pairs:
        lines.append(
            f"- {item['pair_id']} ({item['dimension']}): {item['decision_a']} vs {item['decision_b']} "
            f"differentiated={item['differentiated']} sensitive={item['evidence_sensitive']}"
        )
    lines.extend(
        [
            "",
            "## 12. Failure analysis",
            "",
            f"ADAPT inappropriate decisions: {len(failures)}",
            "",
        ]
    )
    for item in failures:
        lines.append(
            f"- `{item['scenario_id']}` decision=`{item['decision']}` error=`{item.get('error_type')}`"
        )
    lines.extend(["", f"Baseline inappropriate decisions: {len(base_failures)}", ""])
    for item in base_failures[:20]:
        lines.append(
            f"- `{item['scenario_id']}` decision=`{item['decision']}` error=`{item.get('error_type')}`"
        )
    if len(base_failures) > 20:
        lines.append(f"- ... {len(base_failures) - 20} more")
    lines.extend(
        [
            "",
            "## 13. Representative examples",
            "",
            _example_block(
                "ADAPT strong mastery",
                by_id.get(mastery["scenario_id"]) if mastery else None,
            ),
            _example_block(
                "ADAPT lucky guess",
                by_id.get(lucky["scenario_id"]) if lucky else None,
            ),
            _example_block(
                "ADAPT repeated misconception",
                by_id.get(misc["scenario_id"]) if misc else None,
            ),
            _example_block("Counterfactual pair", cf_pair),
            _example_block(
                "ADAPT failure (if any)",
                by_id.get(failure["scenario_id"]) if failure else None,
            ),
            "## 14. Limitations",
            "",
            "- Deterministic keyword analysis, not an LLM tutor.",
            "- One concept (`basic_algebra`) and a small challenge bank.",
            "- CF-P2 cannot match raw accuracy exactly because misconception evidence is expressed as incorrect diagnostic answers.",
            "- Secondary error labels are heuristic.",
            "- This is not a human learning-gain study.",
            "",
            "## 15. Conclusion",
            "",
            f"{verdict}: {verdict_text}",
            "",
            "## 16. Reproducibility information",
            "",
            f"- Benchmark version: {meta.get('benchmark_version')}",
            f"- Random seed: {meta.get('random_seed')}",
            f"- Timestamp: {meta.get('timestamp')}",
            f"- Python: {meta.get('python_version')}",
            f"- Git commit: {meta.get('git_commit')}",
            f"- Scenario count: {meta.get('scenario_count')}",
            "",
        ]
    )
    return "\n".join(lines)
