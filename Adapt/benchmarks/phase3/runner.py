"""Phase 3 benchmark runner.

python -m benchmarks.phase3.runner
"""

from __future__ import annotations

import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from adapt.tutor.tutor import DEFAULT_SEED
from benchmarks.phase3.constants import BENCHMARK_VERSION, RANDOM_SEED
from benchmarks.phase3.execute import make_tutor, run_scenario, run_trajectory
from benchmarks.phase3.metrics import compute_metrics
from benchmarks.phase3.scenarios import SCENARIOS
from benchmarks.phase3.trajectories import TRAJECTORIES

ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = ROOT / "results" / "phase3"


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


def run_counterfactuals(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pairs: dict[str, dict[str, dict[str, Any]]] = {}
    for item in records:
        pair_id = item.get("pair_id")
        role = item.get("pair_role")
        if pair_id and role:
            pairs.setdefault(pair_id, {})[role] = item
    out = []
    expected = {
        "P3-CF-001": "stronger state/strategy vs probe/maintain",
        "P3-CF-002": "continue/increase vs PROBE/REMEDIATE",
        "P3-CF-003": "remain REMEDIATE vs strategy recovery",
    }
    for pair_id, roles in sorted(pairs.items()):
        a = roles.get("A") or {}
        b = roles.get("B") or {}
        differentiated = (
            a.get("final_strategy") != b.get("final_strategy")
            or a.get("next_challenge_ids") != b.get("next_challenge_ids")
            or abs(float(a.get("final_mastery") or 0) - float(b.get("final_mastery") or 0)) >= 0.02
            or a.get("strategies") != b.get("strategies")
        )
        out.append(
            {
                "pair_id": pair_id,
                "decision_a": a.get("final_strategy"),
                "decision_b": b.get("final_strategy"),
                "challenge_a": a.get("final_challenge_id"),
                "challenge_b": b.get("final_challenge_id"),
                "mastery_a": a.get("final_mastery"),
                "mastery_b": b.get("final_mastery"),
                "strategies_a": a.get("strategies"),
                "strategies_b": b.get("strategies"),
                "differentiated": differentiated,
                "expected": expected.get(pair_id, "materially different trajectories"),
            }
        )
    return out


def _pct(metric: dict[str, Any] | None) -> str:
    if not metric:
        return "n/a"
    return str(metric.get("display") or "n/a")


def _wilson(metric: dict[str, Any] | None) -> str:
    if not metric or not metric.get("wilson_95"):
        return "n/a"
    low, high = metric["wilson_95"]
    return f"{low * 100:.1f}–{high * 100:.1f}%"


def render_report(
    *,
    meta: dict[str, Any],
    metrics: dict[str, Any],
    records: list[dict[str, Any]],
    counterfactuals: list[dict[str, Any]],
) -> str:
    fails = [item for item in records if item.get("appropriate") is not True]
    lines = [
        "# Phase 3 — End-to-End Adaptive Tutor Results",
        "",
        "## 1. Research question",
        "",
        "When a learner interacts with ADAPT over multiple steps, does learner evidence",
        "continuously influence learner state, instructional strategy, and subsequent challenge selection?",
        "",
        "## 2. Architecture",
        "",
        "AdaptiveTutor orchestrates EvidenceAnalyzer → StateUpdater → StrategyState →",
        "AdaptiveStrategyEngine → AdaptiveChallengeSelector as one atomic session step.",
        "",
        f"**Benchmark version:** `{meta.get('benchmark_version')}`",
        f"**Timestamp:** {meta.get('timestamp')}",
        f"**Seed:** `{meta.get('seed')}`",
        f"**Python:** {meta.get('python_version')}",
        "",
        "## 3. Benchmark methodology",
        "",
        "Deterministic scripted responses. No LLM. Development and holdout splits are frozen.",
        "The same seed and inputs must reproduce the same decisions, strategy transitions,",
        "challenge IDs, and metrics.",
        "",
        "## 4. Scenario distribution",
        "",
        f"- Sessions + trajectories: {metrics.get('session_count')}",
        f"- Scored steps: {metrics.get('scored_steps')}",
        f"- Longitudinal trajectories: {metrics.get('trajectory_count')}",
        f"- Development appropriateness: {_pct(metrics.get('development_appropriateness'))}",
        f"- Holdout appropriateness: {_pct(metrics.get('holdout_appropriateness'))}",
        "",
        "## 5. Metrics",
        "",
        "| Metric | Result | Wilson 95% |",
        "| --- | --- | --- |",
        f"| M3-001 End-to-end adaptation | {_pct(metrics['M3-001_end_to_end_adaptation'])} | {_wilson(metrics['M3-001_end_to_end_adaptation'])} |",
        f"| M3-002 State-to-strategy causality | {_pct(metrics['M3-002_state_to_strategy_causality'])} | {_wilson(metrics['M3-002_state_to_strategy_causality'])} |",
        f"| M3-003 Strategy-to-challenge consistency | {_pct(metrics['M3-003_strategy_to_challenge_consistency'])} | {_wilson(metrics['M3-003_strategy_to_challenge_consistency'])} |",
        f"| M3-004 Counterfactual differentiation | {_pct(metrics['M3-004_counterfactual_differentiation'])} | {_wilson(metrics['M3-004_counterfactual_differentiation'])} |",
        f"| M3-005 Longitudinal stability | {_pct(metrics['M3-005_longitudinal_stability'])} | {_wilson(metrics['M3-005_longitudinal_stability'])} |",
        f"| M3-006 Recovery | {_pct(metrics['M3-006_recovery'])} | {_wilson(metrics['M3-006_recovery'])} |",
        f"| M3-007 Misconception handling | {_pct(metrics['M3-007_misconception_handling'])} | {_wilson(metrics['M3-007_misconception_handling'])} |",
        f"| M3-008 Trace completeness | {_pct(metrics['M3-008_trace_completeness'])} | {_wilson(metrics['M3-008_trace_completeness'])} |",
        "",
        "## 6. Development results",
        "",
        f"{_pct(metrics.get('development_appropriateness'))}",
        "",
        "## 7. Holdout results",
        "",
        f"{_pct(metrics.get('holdout_appropriateness'))}",
        "",
        "## 8. Counterfactual results",
        "",
    ]
    for item in counterfactuals:
        flag = "PASS" if item.get("differentiated") else "FAIL"
        lines.append(
            f"- `{item['pair_id']}` {flag}: {item.get('decision_a')} vs {item.get('decision_b')} "
            f"(mastery {item.get('mastery_a')} vs {item.get('mastery_b')}) — {item.get('expected')}"
        )
    lines.extend(["", "## 9. Longitudinal results", ""])
    for item in records:
        if item.get("kind") != "trajectory":
            continue
        flag = "PASS" if item.get("appropriate") else "FAIL"
        lines.append(
            f"- `{item['scenario_id']}` {flag} final={item.get('final_strategy')} "
            f"oscillation={item.get('oscillation_violation')} path={item.get('strategies')}"
        )
    lines.extend(["", "## 10. Metamorphic results", ""])
    for key, value in (meta.get("metamorphic") or {}).items():
        lines.append(f"- {key}: {'PASS' if value else 'FAIL'}")
    lines.extend(["", "## 11. Adversarial results", ""])
    for key, value in (meta.get("adversarial") or {}).items():
        lines.append(f"- {key}: {'PASS' if value else 'FAIL'}")
    lines.extend(["", "## 12. Failure cases", ""])
    if not fails:
        lines.append("No scored scenario failed the appropriateness check.")
    else:
        for item in fails:
            lines.append(
                f"- `{item.get('scenario_id')}` split={item.get('split')} "
                f"final={item.get('final_strategy')} expected={item.get('expected_final')}"
            )
    lines.extend(
        [
            "",
            "## 13. Regression results",
            "",
            "Phase 1E, Phase 1F, and Phase 2 runners are executed separately and must remain",
            "reproducible. This runner does not rewrite historical artifacts.",
            "",
            "## 14. Limitations",
            "",
            "- Evidence analysis remains keyword/heuristic based.",
            "- Challenge selection is a deterministic heuristic, not Bayesian optimization.",
            "- Recovery and hysteresis thresholds are inherited from Phase 2.",
            "",
            "## 15. Conclusion",
            "",
            "See docs/phase-3/3.md for the phase transition decision.",
            "",
        ]
    )
    return "\n".join(lines) + "\n"


def _metamorphic_checks(seed: int) -> dict[str, bool]:
    from adapt.tutor.responses import IRRELEVANT_TEXT, build_scripted_response

    tutor_a = make_tutor(seed)
    tutor_b = make_tutor(seed)
    session_a = tutor_a.start_session(
        learner_id="META-A", concept_id="basic_algebra", session_id="META-001",
        initial_challenge="ALG-M-001",
    )
    session_b = tutor_b.start_session(
        learner_id="META-B", concept_id="basic_algebra", session_id="META-001B",
        initial_challenge="ALG-M-001",
    )
    _ = session_a
    ch_a = tutor_a.get_next_challenge("META-001")
    ch_b = tutor_b.get_next_challenge("META-001B")
    base = build_scripted_response(ch_a, "strong_correct", learner_id="META-A", response_id="M-1")
    extra = build_scripted_response(
        ch_b, "strong_correct", learner_id="META-B", response_id="M-1", extra_text=IRRELEVANT_TEXT
    )
    step_a = tutor_a.submit_response("META-001", base)
    step_b = tutor_b.submit_response("META-001B", extra)
    meta001 = step_a.decision == step_b.decision

    tutor_c = make_tutor(seed)
    s1 = tutor_c.start_session(learner_id="META-C", session_id="META-003", initial_challenge="ALG-M-001")
    _ = s1
    ch = tutor_c.get_next_challenge("META-003")
    r1 = build_scripted_response(ch, "strong_correct", learner_id="META-C", response_id="E1")
    r2 = build_scripted_response(ch, "strong_correct", learner_id="META-C", response_id="E2")
    # equivalent answer forms
    from dataclasses import replace

    r2 = replace(r2, answer=f"x = {ch.expected_answer}")
    ev1 = tutor_c.pipeline.analyzer.analyze(r1, ch)
    ev2 = tutor_c.pipeline.analyzer.analyze(r2, ch)
    meta003 = ev1.answer_status == ev2.answer_status

    tutor_d = make_tutor(seed)
    tutor_d.start_session(learner_id="META-D", session_id="META-005", initial_challenge="ALG-M-001")
    ch = tutor_d.get_next_challenge("META-005")
    adv = build_scripted_response(ch, "adversarial_harder", learner_id="META-D", response_id="ADV")
    step = tutor_d.submit_response("META-005", adv)
    meta005 = step.decision.value != "INCREASE"

    tutor_e = make_tutor(seed)
    tutor_e.start_session(learner_id="META-E", session_id="META-004", initial_challenge="ALG-M-001")
    ch = tutor_e.get_next_challenge("META-004")
    dup = build_scripted_response(
        ch, "weak_correct", learner_id="META-E", response_id="DUP", extra_text=(" hello" * 20)
    )
    step = tutor_e.submit_response("META-004", dup)
    meta004 = step.decision.value != "INCREASE" and step.state_after.mastery_estimate < 0.7

    tutor_f = make_tutor(seed)
    tutor_f.start_session(learner_id="META-F", session_id="META-002", initial_challenge="ALG-M-001")
    ch = tutor_f.get_next_challenge("META-002")
    r = build_scripted_response(
        ch, "strong_correct", learner_id="META-F", response_id="MD",
        metadata={"b": 2, "a": 1},
    )
    step1 = tutor_f.submit_response("META-002", r)
    tutor_g = make_tutor(seed)
    tutor_g.start_session(learner_id="META-G", session_id="META-002B", initial_challenge="ALG-M-001")
    ch = tutor_g.get_next_challenge("META-002B")
    r = build_scripted_response(
        ch, "strong_correct", learner_id="META-G", response_id="MD",
        metadata={"a": 1, "b": 2},
    )
    step2 = tutor_g.submit_response("META-002B", r)
    meta002 = step1.decision == step2.decision
    return {
        "M3-META-001": meta001,
        "M3-META-002": meta002,
        "M3-META-003": meta003,
        "M3-META-004": meta004,
        "M3-META-005": meta005,
    }


def _adversarial_checks(seed: int) -> dict[str, bool]:
    from adapt.tutor.responses import ADVERSARIAL_PHRASES, build_scripted_response

    results = {}
    for index, phrase in enumerate(ADVERSARIAL_PHRASES, start=1):
        tutor = make_tutor(seed)
        sid = f"ADV-{index}"
        tutor.start_session(learner_id=sid, session_id=sid, initial_challenge="ALG-M-001")
        ch = tutor.get_next_challenge(sid)
        response = build_scripted_response(
            ch, "weak_correct", learner_id=sid, response_id=f"{sid}-R", extra_text=phrase
        )
        step = tutor.submit_response(sid, response)
        results[phrase] = step.decision.value != "INCREASE"
    return results


def run_benchmark(*, persist: bool = True, seed: int = RANDOM_SEED) -> dict[str, Any]:
    tutor = make_tutor(seed)
    records = [run_scenario(item, tutor=tutor, seed=seed) for item in SCENARIOS]
    records.extend(run_trajectory(item, tutor=make_tutor(seed), seed=seed) for item in TRAJECTORIES)
    counterfactuals = run_counterfactuals(records)
    metrics = compute_metrics(records, counterfactuals)
    metamorphic = _metamorphic_checks(seed)
    adversarial = _adversarial_checks(seed)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    meta = {
        "benchmark_version": BENCHMARK_VERSION,
        "timestamp": timestamp,
        "seed": seed,
        "python_version": platform.python_version(),
        "git_commit": _git_commit(),
        "scenario_count": len(SCENARIOS),
        "trajectory_count": len(TRAJECTORIES),
        "metamorphic": metamorphic,
        "adversarial": adversarial,
        "default_seed": DEFAULT_SEED,
    }
    report = render_report(meta=meta, metrics=metrics, records=records, counterfactuals=counterfactuals)
    trajectories = [item for item in records if item.get("kind") == "trajectory"]
    payload = {
        "meta": meta,
        "metrics": metrics,
        "records": records,
        "counterfactuals": counterfactuals,
        "trajectories": trajectories,
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
            },
            "metrics.json": metrics,
            "trajectories.json": trajectories,
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
    return payload


def main() -> int:
    payload = run_benchmark(persist=True, seed=RANDOM_SEED)
    sys.stdout.write(payload["report"])
    metrics = payload["metrics"]
    completeness = metrics["M3-008_trace_completeness"].get("rate")
    if completeness != 1.0:
        sys.stderr.write("M3-008 trace completeness is below 100%.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
