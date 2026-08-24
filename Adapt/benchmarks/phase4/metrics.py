"""Phase 4 product metrics M4-001 through M4-005."""

from __future__ import annotations

from typing import Any

from benchmarks.phase1e.statistics import wilson_interval
from benchmarks.phase4.expected import TARGETS


def _rate(successes: int, n: int) -> dict[str, Any]:
    interval = wilson_interval(successes, n) if n else None
    return {
        "successes": successes,
        "n": n,
        "rate": None if n == 0 else successes / n,
        "display": "n/a" if n == 0 else f"{successes} / {n} = {100.0 * successes / n:.1f}%",
        "wilson_95": None if interval is None else [round(interval[0], 4), round(interval[1], 4)],
        "target": None,
        "met": None,
    }


def compute_metrics(
    records: list[dict[str, Any]],
    counterfactuals: list[dict[str, Any]],
    restorations: list[dict[str, Any]],
) -> dict[str, Any]:
    sessions = [item for item in records if item.get("kind") == "session"]
    completed = [item for item in sessions if item.get("completed_without_failure")]
    m1 = _rate(len(completed), len(sessions))
    m1["target"] = TARGETS["M4-001"]
    m1["met"] = (m1["rate"] or 0) >= TARGETS["M4-001"]

    preserve_n = sum(item.get("steps", 0) for item in sessions)
    preserve_ok = sum(item.get("preserved_steps", 0) for item in sessions)
    m2 = _rate(preserve_ok, preserve_n)
    m2["target"] = TARGETS["M4-002"]
    m2["met"] = (m2["rate"] or 0) >= TARGETS["M4-002"]

    trace_n = sum(item.get("steps", 0) for item in sessions)
    trace_ok = sum(item.get("trace_complete_steps", 0) for item in sessions)
    m3 = _rate(trace_ok, trace_n)
    m3["target"] = TARGETS["M4-003"]
    m3["met"] = (m3["rate"] or 0) >= TARGETS["M4-003"]

    m4 = _rate(sum(1 for item in counterfactuals if item.get("preserved")), len(counterfactuals))
    m4["target"] = TARGETS["M4-004"]
    m4["met"] = (m4["rate"] or 0) >= TARGETS["M4-004"]

    m5 = _rate(sum(1 for item in restorations if item.get("preserved")), len(restorations))
    m5["target"] = TARGETS["M4-005"]
    m5["met"] = (m5["rate"] or 0) >= TARGETS["M4-005"]

    return {
        "M4-001_task_completion": m1,
        "M4-002_adaptive_result_preservation": m2,
        "M4-003_trace_visibility": m3,
        "M4-004_counterfactual_preservation": m4,
        "M4-005_session_recovery": m5,
        "session_count": len(sessions),
        "step_count": preserve_n,
        "counterfactual_count": len(counterfactuals),
        "recovery_scenario_count": sum(1 for item in sessions if item.get("recovery_scenario")),
        "misconception_scenario_count": sum(1 for item in sessions if item.get("misconception_scenario")),
        "all_targets_met": all(item.get("met") for item in (m1, m2, m3, m4, m5)),
    }
