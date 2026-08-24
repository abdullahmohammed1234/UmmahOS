"""Phase 3 metrics M3-001 through M3-008."""

from __future__ import annotations

from typing import Any

from benchmarks.phase1e.statistics import wilson_interval


def _rate(successes: int, n: int) -> dict[str, Any]:
    interval = wilson_interval(successes, n) if n else None
    return {
        "successes": successes,
        "n": n,
        "rate": None if n == 0 else successes / n,
        "display": "n/a" if n == 0 else f"{successes} / {n} = {100.0 * successes / n:.1f}%",
        "wilson_95": None if interval is None else [round(interval[0], 4), round(interval[1], 4)],
    }


def compute_metrics(
    records: list[dict[str, Any]],
    counterfactuals: list[dict[str, Any]],
) -> dict[str, Any]:
    sessions = [item for item in records if item.get("kind") in {"session", "trajectory"}]
    adapted = [
        item
        for item in sessions
        if item.get("meaningful_evidence") and item.get("n_steps", 0) >= 1
    ]
    m1 = _rate(sum(1 for item in adapted if item.get("appropriate")), len(adapted))

    causal_success = 0
    causal_n = 0
    compat_success = 0
    compat_n = 0
    complete_success = 0
    complete_n = 0
    for item in sessions:
        traces = item.get("traces") or []
        n = len(traces)
        if n == 0:
            continue
        causal_n += n
        causal_success += round(item.get("state_strategy_causal_rate", 1.0) * n)
        compat_n += n
        compat_success += round(item.get("strategy_challenge_compatible_rate", 1.0) * n)
        complete_n += n
        complete_success += round(item.get("trace_complete_rate", 1.0) * n)

    m4 = _rate(
        sum(1 for item in counterfactuals if item.get("differentiated")),
        len(counterfactuals),
    )
    long_records = [item for item in sessions if item.get("kind") == "trajectory"]
    stable = [item for item in long_records if not item.get("oscillation_violation")]
    m5 = _rate(len(stable), len(long_records))
    recovery = [item for item in sessions if item.get("recovery_scenario")]
    m6 = _rate(sum(1 for item in recovery if item.get("recovered")), len(recovery))
    misc = [item for item in sessions if item.get("misconception_scenario")]
    m7 = _rate(sum(1 for item in misc if item.get("misconception_handled")), len(misc))

    development = [item for item in sessions if item.get("split") == "development"]
    holdout = [item for item in sessions if item.get("split") == "holdout"]

    return {
        "M3-001_end_to_end_adaptation": m1,
        "M3-002_state_to_strategy_causality": _rate(int(causal_success), causal_n),
        "M3-003_strategy_to_challenge_consistency": _rate(int(compat_success), compat_n),
        "M3-004_counterfactual_differentiation": m4,
        "M3-005_longitudinal_stability": m5,
        "M3-006_recovery": m6,
        "M3-007_misconception_handling": m7,
        "M3-008_trace_completeness": _rate(int(complete_success), complete_n),
        "development_appropriateness": _rate(
            sum(1 for item in development if item.get("appropriate")), len(development)
        ),
        "holdout_appropriateness": _rate(
            sum(1 for item in holdout if item.get("appropriate")), len(holdout)
        ),
        "scored_steps": complete_n,
        "session_count": len(sessions),
        "trajectory_count": len(long_records),
    }
