"""Phase 12 statistics. Do not claim significance the sample cannot support."""

from __future__ import annotations

from typing import Any

from benchmarks.phase1e.statistics import mcnemar_test, relative_improvement, wilson_interval

MIN_N_FOR_MCNEMAR_NOTE = 30


def paired_binary_summary(
    workflow_ok: list[bool],
    baseline_ok: list[bool],
) -> dict[str, Any]:
    n = min(len(workflow_ok), len(baseline_ok))
    workflow_ok = workflow_ok[:n]
    baseline_ok = baseline_ok[:n]
    successes_w = sum(1 for item in workflow_ok if item)
    successes_b = sum(1 for item in baseline_ok if item)
    n10 = sum(1 for w, b in zip(workflow_ok, baseline_ok) if w and not b)
    n01 = sum(1 for w, b in zip(workflow_ok, baseline_ok) if b and not w)
    n11 = sum(1 for w, b in zip(workflow_ok, baseline_ok) if w and b)
    n00 = sum(1 for w, b in zip(workflow_ok, baseline_ok) if (not w) and (not b))
    rate_w = successes_w / n if n else None
    rate_b = successes_b / n if n else None
    abs_diff = None if rate_w is None or rate_b is None else rate_w - rate_b
    rel_diff = relative_improvement(rate_w, rate_b)
    test = mcnemar_test(n10, n01)
    significant = bool(
        n >= MIN_N_FOR_MCNEMAR_NOTE
        and test.get("p_value") is not None
        and test["p_value"] < 0.05
        and (n10 + n01) > 0
    )
    note = (
        "McNemar p-value is descriptive. "
        + (
            f"n={n} paired scenarios."
            if n >= MIN_N_FOR_MCNEMAR_NOTE
            else f"n={n} is small; do not treat p as confirmatory."
        )
    )
    if not significant:
        note += " Difference is not claimed as statistically significant."
    return {
        "n": n,
        "adapt_score": rate_w,
        "baseline_score": rate_b,
        "adapt_successes": successes_w,
        "baseline_successes": successes_b,
        "absolute_difference": abs_diff,
        "relative_difference": rel_diff,
        "wilson_adapt": wilson_interval(successes_w, n),
        "wilson_baseline": wilson_interval(successes_b, n),
        "mcnemar": test,
        "contingency": {"n11": n11, "n10": n10, "n01": n01, "n00": n00},
        "statistically_significant": significant,
        "note": note,
    }
