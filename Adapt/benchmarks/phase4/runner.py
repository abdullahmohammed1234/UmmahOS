"""Phase 4 product benchmark runner.

python -m benchmarks.phase4.runner
"""

from __future__ import annotations

import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from adapt.product.service import ProductService
from adapt.tutor.tutor import DEFAULT_SEED
from benchmarks.phase4.expected import (
    BENCHMARK_VERSION,
    MIN_COUNTERFACTUALS,
    MIN_MISCONCEPTION,
    MIN_RECOVERY,
    MIN_SESSIONS,
    MIN_STEPS,
    RANDOM_SEED,
)
from benchmarks.phase4.metrics import compute_metrics
from benchmarks.phase4.scenarios import COUNTERFACTUALS, SCENARIOS
from tests.phase4.helpers import run_kinds_through_product, run_kinds_through_tutor, scripted_submit

ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = ROOT / "results" / "phase4"


def _git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip() or "unavailable"
    except OSError:
        return "unavailable"
    return "unavailable"


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def run_session(spec: dict[str, Any], *, seed: int) -> dict[str, Any]:
    kinds = tuple(spec["kinds"])
    topic_id = spec["topic_id"]
    initial = spec.get("initial_challenge")
    concept_id = "fractions" if topic_id == "fractions" else "basic_algebra"
    failed = False
    message = None
    try:
        service, session, results = run_kinds_through_product(
            kinds,
            topic_id=topic_id,
            session_id=f"{spec['id']}-P",
            learner_id=f"{spec['id']}-L",
            initial_challenge=initial,
            service=ProductService(seed=seed),
            max_steps=len(kinds),
        )
        _, tutor_session, traces = run_kinds_through_tutor(
            kinds,
            learner_id=f"{spec['id']}-T",
            session_id=f"{spec['id']}-T",
            concept_id=concept_id,
            initial_challenge=initial,
            seed=seed,
        )
        product_decisions = [item["result"]["adaptation"]["decision"] for item in results]
        tutor_decisions = [item.decision.value for item in traces]
        product_next = [item["research"]["next_challenge"]["challenge_id"] for item in results]
        tutor_next = [item.next_challenge_id for item in traces]
        preserved_steps = sum(
            1
            for p, t, pn, tn in zip(product_decisions, tutor_decisions, product_next, tutor_next, strict=True)
            if p == t and pn == tn
        )
        trace = service.get_trace(session["session_id"])
        trace_complete_steps = sum(1 for link in trace["chain"] if link["complete"])
        _ = tutor_session
        return {
            "kind": "session",
            "scenario_id": spec["id"],
            "topic_id": topic_id,
            "steps": len(kinds),
            "completed_without_failure": True,
            "product_decisions": product_decisions,
            "tutor_decisions": tutor_decisions,
            "preserved_steps": preserved_steps,
            "trace_complete_steps": trace_complete_steps,
            "recovery_scenario": bool(spec.get("recovery_scenario")),
            "misconception_scenario": bool(spec.get("misconception_scenario")),
            "final_strategy": product_decisions[-1] if product_decisions else None,
        }
    except Exception as exc:  # noqa: BLE001 — benchmark must record application failures
        failed = True
        message = f"{type(exc).__name__}: {exc}"
        return {
            "kind": "session",
            "scenario_id": spec["id"],
            "topic_id": spec["topic_id"],
            "steps": len(kinds),
            "completed_without_failure": not failed,
            "error": message,
            "product_decisions": [],
            "tutor_decisions": [],
            "preserved_steps": 0,
            "trace_complete_steps": 0,
            "recovery_scenario": bool(spec.get("recovery_scenario")),
            "misconception_scenario": bool(spec.get("misconception_scenario")),
            "final_strategy": None,
        }


def run_counterfactual(spec: dict[str, Any], *, seed: int) -> dict[str, Any]:
    service = ProductService(seed=seed)
    payload = service.run_counterfactual(spec)
    kinds_a = tuple(spec["learner_a"]["kinds"])
    kinds_b = tuple(spec["learner_b"]["kinds"])
    _, _, traces_a = run_kinds_through_tutor(
        kinds_a,
        session_id=f"{spec['id']}-TA",
        concept_id=spec.get("concept_id") or "basic_algebra",
        initial_challenge=spec["challenge_id"],
        seed=seed,
    )
    _, _, traces_b = run_kinds_through_tutor(
        kinds_b,
        session_id=f"{spec['id']}-TB",
        learner_id="TB",
        concept_id=spec.get("concept_id") or "basic_algebra",
        initial_challenge=spec["challenge_id"],
        seed=seed,
    )
    engine_diff = traces_a[-1].decision != traces_b[-1].decision or traces_a[-1].next_challenge_id != traces_b[-1].next_challenge_id
    product_diff = payload["differentiated"]
    preserved = (
        product_diff is True
        and engine_diff is True
        and payload["learner_a"]["final_decision"] == traces_a[-1].decision.value
        and payload["learner_b"]["final_decision"] == traces_b[-1].decision.value
        and payload["learner_a"]["final_challenge"] == traces_a[-1].next_challenge_id
        and payload["learner_b"]["final_challenge"] == traces_b[-1].next_challenge_id
    )
    return {
        "pair_id": spec["id"],
        "decision_a": payload["learner_a"]["final_decision"],
        "decision_b": payload["learner_b"]["final_decision"],
        "challenge_a": payload["learner_a"]["final_challenge"],
        "challenge_b": payload["learner_b"]["final_challenge"],
        "engine_decision_a": traces_a[-1].decision.value,
        "engine_decision_b": traces_b[-1].decision.value,
        "differentiated": product_diff,
        "engine_differentiated": engine_diff,
        "preserved": preserved,
    }


def run_restoration(spec: dict[str, Any], *, seed: int) -> dict[str, Any]:
    kinds = tuple(spec["kinds"])
    topic_id = spec["topic_id"]
    initial = spec["initial_challenge"]
    mid = max(1, len(kinds) // 2)
    service = ProductService(seed=seed)
    sid = spec["id"]
    view = service.create_session(
        topic_id=topic_id,
        learner_id=f"{sid}-r",
        session_id=sid,
        initial_challenge=initial,
        max_steps=len(kinds),
    )
    for kind in kinds[:mid]:
        scripted_submit(service, view["session_id"], kind)
    snap = service.snapshot(view["session_id"])
    control = ProductService(seed=seed)
    control.create_session(
        topic_id=topic_id,
        learner_id=f"{sid}-c",
        session_id=f"{sid}-C",
        initial_challenge=initial,
        max_steps=len(kinds),
    )
    for kind in kinds:
        scripted_submit(control, f"{sid}-C", kind)
    restored = ProductService(seed=seed)
    restored.restore(snap)
    for kind in kinds[mid:]:
        scripted_submit(restored, view["session_id"], kind)
    restored_decisions = [item.decision.value for item in restored.tutor.get_trace(view["session_id"])]
    control_decisions = [item.decision.value for item in control.tutor.get_trace(f"{sid}-C")]
    restored_next = [item.next_challenge_id for item in restored.tutor.get_trace(view["session_id"])]
    control_next = [item.next_challenge_id for item in control.tutor.get_trace(f"{sid}-C")]
    return {
        "id": sid,
        "preserved": restored_decisions == control_decisions and restored_next == control_next,
        "restored_decisions": restored_decisions,
        "control_decisions": control_decisions,
    }


RESTORES = (
    {"id": "P4-RESTORE-001", "topic_id": "algebra", "initial_challenge": "ALG-M-001", "kinds": ("strong_correct", "weak_correct", "strong_correct", "moderate_correct")},
    {"id": "P4-RESTORE-002", "topic_id": "algebra", "initial_challenge": "ALG-D-001", "kinds": ("strong_correct",) * 6},
    {"id": "P4-RESTORE-003", "topic_id": "fractions", "initial_challenge": "FR-D-001", "kinds": ("weak_correct", "strong_correct", "strong_correct", "misconception")},
    {"id": "P4-RESTORE-004", "topic_id": "algebra", "initial_challenge": "ALG-M-002", "kinds": ("strong_correct", "strong_correct", "misconception", "strong_correct")},
    {"id": "P4-RESTORE-005", "topic_id": "fractions", "initial_challenge": "FR-M-001", "kinds": ("moderate_correct", "strong_correct", "weak_correct", "strong_correct")},
)


def _pct(metric: dict[str, Any] | None) -> str:
    if not metric:
        return "n/a"
    return str(metric.get("display") or "n/a")


def render_report(*, meta: dict[str, Any], metrics: dict[str, Any], records: list[dict[str, Any]], counterfactuals: list[dict[str, Any]], restorations: list[dict[str, Any]]) -> str:
    fails = [item for item in records if not item.get("completed_without_failure")]
    preserve_fails = [item for item in records if item.get("preserved_steps", 0) != item.get("steps", 0)]
    lines = [
        "# Phase 4 — Learner Experience & Demo Product Results",
        "",
        "## 1. Question",
        "",
        "Can a real learner experience ADAPT's adaptation clearly, naturally, and convincingly,",
        "without the product layer inventing adaptive decisions?",
        "",
        f"**Benchmark version:** `{meta.get('benchmark_version')}`",
        f"**Timestamp:** {meta.get('timestamp')}",
        f"**Seed:** `{meta.get('seed')}`",
        f"**Python:** {meta.get('python_version')}",
        "",
        "## 2. Coverage",
        "",
        f"- Sessions: {metrics.get('session_count')} (minimum {MIN_SESSIONS})",
        f"- Interaction steps: {metrics.get('step_count')} (minimum {MIN_STEPS})",
        f"- Counterfactual pairs: {metrics.get('counterfactual_count')} (minimum {MIN_COUNTERFACTUALS})",
        f"- Recovery scenarios: {metrics.get('recovery_scenario_count')} (minimum {MIN_RECOVERY})",
        f"- Misconception scenarios: {metrics.get('misconception_scenario_count')} (minimum {MIN_MISCONCEPTION})",
        "",
        "## 3. Metrics",
        "",
        "| Metric | Result | Target | Met |",
        "| --- | --- | --- | --- |",
        f"| M4-001 Task completion | {_pct(metrics['M4-001_task_completion'])} | ≥ 95% | {metrics['M4-001_task_completion']['met']} |",
        f"| M4-002 Adaptive result preservation | {_pct(metrics['M4-002_adaptive_result_preservation'])} | 100% | {metrics['M4-002_adaptive_result_preservation']['met']} |",
        f"| M4-003 Trace visibility | {_pct(metrics['M4-003_trace_visibility'])} | 100% | {metrics['M4-003_trace_visibility']['met']} |",
        f"| M4-004 Counterfactual preservation | {_pct(metrics['M4-004_counterfactual_preservation'])} | 100% | {metrics['M4-004_counterfactual_preservation']['met']} |",
        f"| M4-005 Session recovery | {_pct(metrics['M4-005_session_recovery'])} | 100% | {metrics['M4-005_session_recovery']['met']} |",
        "",
        "## 4. Counterfactuals",
        "",
    ]
    for item in counterfactuals:
        flag = "PASS" if item.get("preserved") else "FAIL"
        lines.append(
            f"- `{item['pair_id']}` {flag}: {item.get('decision_a')} vs {item.get('decision_b')} "
            f"(engine {item.get('engine_decision_a')} vs {item.get('engine_decision_b')})"
        )
    lines.extend(["", "## 5. Restorations", ""])
    for item in restorations:
        lines.append(f"- `{item.get('id')}` {'PASS' if item.get('preserved') else 'FAIL'}: {item.get('restored_decisions')}")
    lines.extend(["", "## 6. Failures", ""])
    if not fails and not preserve_fails:
        lines.append("No application-level session failed completion or preservation.")
    else:
        for item in fails:
            lines.append(f"- `{item.get('scenario_id')}` failed: {item.get('error')}")
        for item in preserve_fails:
            lines.append(
                f"- `{item.get('scenario_id')}` preservation {item.get('preserved_steps')}/{item.get('steps')}"
            )
    lines.extend(
        [
            "",
            "## 7. Usability",
            "",
            "PENDING — no formative human test was executed in this automated run.",
            "",
            "## 8. Conclusion",
            "",
            "See docs/phase-4/4.md for the phase transition decision.",
            "",
        ]
    )
    return "\n".join(lines) + "\n"


def run_benchmark(*, persist: bool = True, seed: int = RANDOM_SEED) -> dict[str, Any]:
    records = [run_session(item, seed=seed) for item in SCENARIOS]
    counterfactuals = [run_counterfactual(item, seed=seed) for item in COUNTERFACTUALS]
    restorations = [run_restoration(item, seed=seed) for item in RESTORES]
    metrics = compute_metrics(records, counterfactuals, restorations)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    meta = {
        "benchmark_version": BENCHMARK_VERSION,
        "timestamp": timestamp,
        "seed": seed,
        "python_version": platform.python_version(),
        "git_commit": _git_commit(),
        "default_seed": DEFAULT_SEED,
        "session_count": len(SCENARIOS),
        "counterfactual_count": len(COUNTERFACTUALS),
        "coverage_ok": (
            len(SCENARIOS) >= MIN_SESSIONS
            and metrics["step_count"] >= MIN_STEPS
            and len(COUNTERFACTUALS) >= MIN_COUNTERFACTUALS
            and metrics["recovery_scenario_count"] >= MIN_RECOVERY
            and metrics["misconception_scenario_count"] >= MIN_MISCONCEPTION
        ),
    }
    report = render_report(
        meta=meta,
        metrics=metrics,
        records=records,
        counterfactuals=counterfactuals,
        restorations=restorations,
    )
    payload = {
        "meta": meta,
        "metrics": metrics,
        "records": records,
        "counterfactuals": counterfactuals,
        "restorations": restorations,
        "report": report,
    }
    if persist:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        run_dir = RESULTS_DIR / "runs" / timestamp
        run_dir.mkdir(parents=True, exist_ok=True)
        files = {
            "raw_results.json": {
                "meta": meta,
                "records": records,
                "counterfactuals": counterfactuals,
                "restorations": restorations,
            },
            "metrics.json": metrics,
            "report.md": report,
        }
        for name, content in files.items():
            target = RESULTS_DIR / name
            run_target = run_dir / name
            if name.endswith(".md"):
                target.write_text(content, encoding="utf-8")
                run_target.write_text(content, encoding="utf-8")
            else:
                text = json.dumps(_jsonable(content), indent=2, sort_keys=True)
                target.write_text(text, encoding="utf-8")
                run_target.write_text(text, encoding="utf-8")
        usability = (
            "# Phase 4 formative usability\n\n"
            "Status: PENDING\n\n"
            "No human usability test was executed during this automated Phase 4 run.\n"
            "Results below must not be invented.\n\n"
            "| Question | Result |\n"
            "| --- | --- |\n"
            "| Can they start a session? | PENDING |\n"
            "| Can they answer without explanation? | PENDING |\n"
            "| Do they understand why the challenge changed? | PENDING |\n"
            "| Can they identify that ADAPT adapted? | PENDING |\n"
            "| Can they complete the session? | PENDING |\n"
        )
        (RESULTS_DIR / "usability.md").write_text(usability, encoding="utf-8")
        (run_dir / "usability.md").write_text(usability, encoding="utf-8")
    return payload


def main() -> int:
    payload = run_benchmark(persist=True, seed=RANDOM_SEED)
    sys.stdout.write(payload["report"])
    metrics = payload["metrics"]
    if not metrics.get("all_targets_met"):
        sys.stderr.write("One or more Phase 4 metric targets were not met.\n")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
