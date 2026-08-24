"""Phase 12 Gemini workflow benchmark.

python -m benchmarks.phase12.runner
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
for path in (str(SRC), str(ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)

from adapt.eval.llm.criteria import prompt_score, select_prompt
from adapt.llm.analyzer import LLMEvidenceAnalyzer
from adapt.llm.baseline import SinglePromptBaseline
from adapt.llm.config import WORKFLOW_VERSION, load_settings
from adapt.llm.fallback import SOURCE_GEMINI
from adapt.llm.prompts import EVIDENCE_PROMPT_IDS, PROMPT_EXPERIMENT
from adapt.llm.simulator import PromptSimulatorClient
from adapt.llm.workflow import attach_adapt_nodes
from adapt.models.enums import LearnerConfidence
from adapt.models.learner_response import LearnerResponse
from adapt.tutor.challenge_bank import PHASE3_BANK
from adapt.tutor.tutor import AdaptiveTutor
from benchmarks.phase12.expected import BENCHMARK_VERSION, HOLDOUT_IDS, RANDOM_SEED, SCENARIO_VERSION
from benchmarks.phase12.metrics import compute_metrics, evidence_match, injection_resisted, strategy_appropriate
from benchmarks.phase12.scenarios import (
    Phase12Scenario,
    SCENARIOS,
    counterfactual_pairs,
    development_scenarios,
    holdout_scenarios,
    _arith_text,
    _arith_wrong,
    _misc_text,
    _strong_text,
    _wrong,
)
from benchmarks.phase12.statistics import paired_binary_summary

RESULTS_DIR = ROOT / "results" / "phase12"


def _bank(challenge):
    if any(item.challenge_id == challenge.challenge_id for item in PHASE3_BANK):
        return PHASE3_BANK
    return (challenge,) + PHASE3_BANK


def _materialize(scenario: Phase12Scenario, challenge) -> LearnerResponse:
    if challenge.challenge_id == scenario.challenge.challenge_id:
        return scenario.learner_response(
            learner_id="p12-learner",
            response_id=f"{scenario.scenario_id}-R",
        )
    family = scenario.family
    role = scenario.pair_role
    confidence = scenario.confidence
    approach = scenario.approach
    if family in {"A", "J"} or (family == "G" and role == "weak"):
        answer = challenge.expected_answer or scenario.answer
        explanation = scenario.explanation
    elif family in {"B"} or (family == "G" and role == "strong") or (family == "F" and role == "high"):
        answer = challenge.expected_answer or scenario.answer
        explanation = _strong_text(challenge)
    elif family == "F" and role == "low":
        answer = challenge.expected_answer or scenario.answer
        explanation = _strong_text(challenge)
    elif family in {"C", "I"}:
        answer = _arith_wrong(challenge)
        explanation = _arith_text(challenge)
    elif family in {"D", "H"}:
        answer = _wrong(challenge)
        explanation = _misc_text(challenge)
    else:
        answer = challenge.expected_answer or scenario.answer
        explanation = scenario.explanation
    reasoning_parts = [p for p in (approach, explanation) if p]
    return LearnerResponse(
        response_id=f"{scenario.scenario_id}-R",
        learner_id="p12-learner",
        concept_id=challenge.concept_id,
        challenge_id=challenge.challenge_id,
        answer=answer,
        reasoning=" ".join(reasoning_parts) or None,
        learner_confidence=LearnerConfidence(confidence),
        metadata={"approach": approach, "explanation": explanation, "scenario_id": scenario.scenario_id},
    )


def _history_response(session, scenario: Phase12Scenario, index: int) -> LearnerResponse:
    challenge = session.current_challenge
    template = scenario.history[index]
    if scenario.family == "I":
        answer = challenge.expected_answer or template["answer"]
        explanation = _strong_text(challenge)
        confidence = "HIGH"
        approach = "I worked it out"
    else:
        answer = _wrong(challenge)
        explanation = _misc_text(challenge)
        confidence = str(template.get("confidence") or "HIGH")
        approach = template.get("approach")
    reasoning_parts = [p for p in (approach, explanation) if p]
    return LearnerResponse(
        response_id=f"{scenario.scenario_id}-H-{index+1:02d}",
        learner_id="p12-learner",
        concept_id=challenge.concept_id,
        challenge_id=challenge.challenge_id,
        answer=str(answer),
        reasoning=" ".join(reasoning_parts) or None,
        learner_confidence=LearnerConfidence(confidence),
        metadata={"approach": approach, "explanation": explanation, "history": True},
    )


def run_workflow_scenario(
    scenario: Phase12Scenario,
    *,
    client,
    prompt_id: str,
    seed: int = RANDOM_SEED,
) -> dict[str, Any]:
    analyzer = LLMEvidenceAnalyzer(client=client, prompt_id=prompt_id)
    tutor = AdaptiveTutor(bank=_bank(scenario.challenge), analyzer=analyzer, seed=seed)
    session = tutor.start_session(
        learner_id="p12-learner",
        concept_id=scenario.challenge.concept_id,
        session_id=f"P12-{prompt_id}-{scenario.scenario_id}",
        initial_challenge=scenario.challenge,
    )
    for index in range(len(scenario.history)):
        live = tutor.get_session(session.session_id)
        tutor.submit_response(session.session_id, _history_response(live, scenario, index))
    live = tutor.get_session(session.session_id)
    target = _materialize(scenario, live.current_challenge)
    step = tutor.submit_response(session.session_id, target)
    workflow = analyzer.last_result
    parsed = None if workflow is None else workflow.parsed
    leak = False
    if parsed:
        leak = any(key in parsed for key in ("strategy", "next_action", "decision", "adaptation"))
    extraction = evidence_match(parsed, scenario.expected) if parsed else {"ok": False, "hits": 0, "total": 5, "fields": {}}
    decision = step.decision.value
    appropriate = strategy_appropriate(decision, scenario.expected)
    nodes = [] if workflow is None else [node.id for node in workflow.nodes]
    traceable = bool(workflow) and {"1", "2", "3"}.issubset(set(nodes))
    if workflow is not None:
        attach_adapt_nodes(
            workflow,
            state={
                "mastery": step.state_after.mastery_estimate,
                "uncertainty": step.state_after.uncertainty.value,
                "evidence_strength": step.state_after.evidence_strength.value,
            },
            strategy={"decision": decision, "reason": step.reason},
            challenge={"challenge_id": step.next_challenge.challenge_id},
            feedback={"noticed": True},
        )
        traceable = {"1", "2", "3", "4", "5", "6", "7"}.issubset({node.id for node in workflow.nodes})
    row = {
        "scenario_id": scenario.scenario_id,
        "family": scenario.family,
        "kind": scenario.kind,
        "split": scenario.split,
        "pair_id": scenario.pair_id,
        "pair_role": scenario.pair_role,
        "prompt_id": prompt_id,
        "experiment": PROMPT_EXPERIMENT.get(prompt_id),
        "source": None if workflow is None else workflow.source,
        "validation_ok": False if workflow is None else workflow.validation_ok,
        "failure_code": None if workflow is None else workflow.failure_code,
        "llm_evidence": parsed,
        "adapt_evidence": step.evidence.to_dict(),
        "adapt_strategy": decision,
        "next_challenge_id": step.next_challenge.challenge_id,
        "mastery": step.state_after.mastery_estimate,
        "extraction_ok": extraction["ok"],
        "extraction": extraction,
        "adapt_appropriate": appropriate,
        "strategy_leak": leak,
        "traceable": traceable,
        "workflow": None if workflow is None else workflow.to_dict(),
        "human_input": {
            "answer": target.answer,
            "confidence": target.learner_confidence.value,
            "reasoning": target.reasoning,
        },
    }
    row["injection_ok"] = injection_resisted(row) if scenario.family == "J" else None
    return row


def run_baseline_scenario(scenario: Phase12Scenario, *, client) -> dict[str, Any]:
    baseline = SinglePromptBaseline(client=client)
    response = scenario.learner_response(learner_id="p12-learner", response_id=f"{scenario.scenario_id}-B")
    result = baseline.run(response, scenario.challenge)
    appropriate = strategy_appropriate(result.next_action, scenario.expected)
    injection_ok = True
    if scenario.family == "J":
        injection_ok = result.next_action != "INCREASE"
    return {
        "scenario_id": scenario.scenario_id,
        "family": scenario.family,
        "next_action": result.next_action,
        "mastery": result.mastery,
        "valid": result.valid,
        "baseline_appropriate": appropriate,
        "injection_ok": injection_ok if scenario.family == "J" else None,
        "raw": result.to_dict(),
    }


def _annotate_pairs(rows: list[dict[str, Any]], scenarios: tuple[Phase12Scenario, ...]) -> None:
    by_id = {row["scenario_id"]: row for row in rows}
    for left, right in counterfactual_pairs(scenarios):
        a = by_id.get(left.scenario_id)
        b = by_id.get(right.scenario_id)
        if not a or not b:
            continue
        ev_a = a.get("llm_evidence") or {}
        ev_b = b.get("llm_evidence") or {}
        evidence_diff = ev_a != ev_b and bool(ev_a) and bool(ev_b)
        if not evidence_diff:
            evidence_diff = (a.get("adapt_evidence") or {}) != (b.get("adapt_evidence") or {})
        a["counterfactual_sensitive"] = evidence_diff
        b["counterfactual_sensitive"] = evidence_diff
        differentiated = (
            a.get("adapt_strategy") != b.get("adapt_strategy")
            or a.get("next_challenge_id") != b.get("next_challenge_id")
            or abs(float(a.get("mastery") or 0) - float(b.get("mastery") or 0)) >= 0.02
        )
        a["adapt_differentiated"] = differentiated
        b["adapt_differentiated"] = differentiated


def _criteria_from_rows(rows: list[dict[str, Any]]) -> dict[str, float]:
    n = len(rows) or 1
    injection = [row for row in rows if row.get("family") == "J"]
    cf = [row for row in rows if row.get("counterfactual_sensitive") is not None]
    return {
        "structured_output_validity": sum(1 for row in rows if row.get("validation_ok")) / n,
        "evidence_extraction_accuracy": sum(1 for row in rows if row.get("extraction_ok")) / n,
        "prompt_injection_robustness": (
            1.0
            if not injection
            else sum(1 for row in injection if row.get("injection_ok")) / len(injection)
        ),
        "no_strategy_leakage": sum(1 for row in rows if not row.get("strategy_leak")) / n,
        "counterfactual_sensitivity": (
            0.0 if not cf else sum(1 for row in cf if row.get("counterfactual_sensitive")) / len(cf)
        ),
    }


def run_prompt_set(
    scenarios: tuple[Phase12Scenario, ...],
    prompt_id: str,
    *,
    evidence_client=None,
    baseline_client=None,
) -> dict[str, Any]:
    evidence_client = evidence_client or PromptSimulatorClient(mode="evidence")
    baseline_client = baseline_client or PromptSimulatorClient(mode="baseline")
    rows = [
        run_workflow_scenario(scenario, client=evidence_client, prompt_id=prompt_id)
        for scenario in scenarios
    ]
    _annotate_pairs(rows, scenarios)
    baseline_rows = [run_baseline_scenario(scenario, client=baseline_client) for scenario in scenarios]
    metrics = compute_metrics(rows, baseline_rows=baseline_rows)
    criteria = _criteria_from_rows(rows)
    paired = paired_binary_summary(
        [bool(row.get("adapt_appropriate")) for row in rows],
        [bool(row.get("baseline_appropriate")) for row in baseline_rows],
    )
    return {
        "prompt_id": prompt_id,
        "experiment": PROMPT_EXPERIMENT.get(prompt_id),
        "n": len(rows),
        "rows": rows,
        "baseline_rows": baseline_rows,
        "metrics": metrics,
        "criteria": criteria,
        "score": prompt_score(criteria),
        "paired": paired,
    }


def run_benchmark(*, persist: bool = True, live: bool = False) -> dict[str, Any]:
    settings = load_settings()
    evidence_client = PromptSimulatorClient(mode="evidence")
    baseline_client = PromptSimulatorClient(mode="baseline")
    backend = "prompt-simulator"
    model = evidence_client.model
    if live:
        from adapt.llm.gemini import GeminiClient

        if not settings.credentials_present:
            raise RuntimeError("Live benchmark requested but GEMINI_API_KEY is not configured")
        evidence_client = GeminiClient(settings=settings)
        baseline_client = GeminiClient(settings=settings)
        backend = "gemini"
        model = settings.model

    development = development_scenarios()
    holdout = holdout_scenarios()
    dev_results = {}
    for prompt_id in EVIDENCE_PROMPT_IDS:
        dev_results[prompt_id] = run_prompt_set(
            development,
            prompt_id,
            evidence_client=evidence_client,
            baseline_client=baseline_client,
        )
        # drop bulky rows from the selection payload copy
    selection = select_prompt(
        {key: {"criteria": value["criteria"]} for key, value in dev_results.items()}
    )
    selected = selection["selected_prompt_id"]
    holdout_result = run_prompt_set(
        holdout,
        selected,
        evidence_client=evidence_client,
        baseline_client=baseline_client,
    )
    full_selected_dev = dev_results[selected]
    now = datetime.now(timezone.utc)
    payload = {
        "meta": {
            "benchmark_version": BENCHMARK_VERSION,
            "scenario_version": SCENARIO_VERSION,
            "workflow_version": WORKFLOW_VERSION,
            "seed": RANDOM_SEED,
            "backend": backend,
            "model": model,
            "temperature": 0.0 if backend == "prompt-simulator" else settings.temperature,
            "prompt_versions": list(EVIDENCE_PROMPT_IDS),
            "selected_prompt_id": selected,
            "holdout_ids": sorted(HOLDOUT_IDS),
            "timestamp": now.isoformat(),
            "n_scenarios": len(SCENARIOS),
            "n_development": len(development),
            "n_holdout": len(holdout),
            "n_standard": sum(1 for item in SCENARIOS if item.kind == "standard"),
            "n_counterfactual": sum(1 for item in SCENARIOS if item.kind == "counterfactual"),
            "n_adversarial": sum(1 for item in SCENARIOS if item.kind == "adversarial"),
            "live": live,
        },
        "development": {
            prompt_id: {
                "criteria": result["criteria"],
                "score": result["score"],
                "metrics": result["metrics"],
                "paired": result["paired"],
                "experiment": result["experiment"],
            }
            for prompt_id, result in dev_results.items()
        },
        "selection": selection,
        "holdout": {
            "prompt_id": selected,
            "criteria": holdout_result["criteria"],
            "score": holdout_result["score"],
            "metrics": holdout_result["metrics"],
            "paired": holdout_result["paired"],
            "rows": holdout_result["rows"],
            "baseline_rows": holdout_result["baseline_rows"],
        },
        "development_rows_selected": full_selected_dev["rows"],
        "development_baseline_selected": full_selected_dev["baseline_rows"],
    }
    report = render_report(payload)
    payload["report"] = report
    if persist:
        stamp = now.strftime("%Y-%m-%dT%H%M%SZ")
        run_dir = RESULTS_DIR / "runs" / stamp
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "metrics.json").write_text(json.dumps(_jsonable(payload), indent=2), encoding="utf-8")
        (run_dir / "report.md").write_text(report, encoding="utf-8")
        summary_path = RESULTS_DIR / "report.md"
        if not summary_path.exists():
            summary_path.write_text(report, encoding="utf-8")
            (RESULTS_DIR / "metrics.json").write_text(
                json.dumps(_jsonable(payload), indent=2), encoding="utf-8"
            )
        payload["meta"]["artifact_dir"] = str(run_dir.relative_to(ROOT)).replace("\\", "/")
    return payload


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, float):
        return value
    return value


def render_report(payload: dict[str, Any]) -> str:
    meta = payload["meta"]
    selection = payload["selection"]
    holdout = payload["holdout"]
    paired = holdout["paired"]
    lines = [
        "# Phase 12 benchmark report",
        "",
        f"Status: executed ({meta['backend']})",
        f"Scenario version: {meta['scenario_version']}",
        f"Workflow version: {meta['workflow_version']}",
        f"Seed: {meta['seed']}",
        f"Model / backend: {meta['model']} / {meta['backend']}",
        f"Selected prompt: {meta['selected_prompt_id']}",
        f"n scenarios: {meta['n_scenarios']} (development {meta['n_development']}, holdout {meta['n_holdout']})",
        "",
        "## Honesty",
        "",
        "- This file records a workflow-vs-baseline comparison of evidence extraction and adaptive decisions.",
        "- It is not a learning-gain result. Phase 5 remains INCONCLUSIVE (n = 0).",
        "- Live Gemini is used only when `backend = gemini`. Simulator runs are labeled as such.",
        "",
        "## Prompt selection (development)",
        "",
    ]
    for prompt_id, result in payload["development"].items():
        crit = result["criteria"]
        lines.append(
            f"- {prompt_id} ({result['experiment']}): score={result['score']:.3f} "
            f"validity={crit['structured_output_validity']:.3f} "
            f"accuracy={crit['evidence_extraction_accuracy']:.3f} "
            f"injection={crit['prompt_injection_robustness']:.3f}"
        )
    lines.extend(
        [
            "",
            f"Selected by frozen criteria {selection['criteria_version']}: **{selection['selected_prompt_id']}**.",
            "",
            "## Holdout (single evaluation of the selected prompt)",
            "",
            f"- Evidence extraction accuracy: {holdout['metrics']['M12-001_evidence_extraction_accuracy']['rate']}",
            f"- Structured output validity: {holdout['metrics']['M12-002_structured_output_validity']['rate']}",
            f"- Counterfactual sensitivity: {holdout['metrics']['M12-003_counterfactual_sensitivity']['rate']}",
            f"- ADAPT decision differentiation: {holdout['metrics']['M12-004_adapt_decision_differentiation']['rate']}",
            f"- Prompt injection robustness: {holdout['metrics']['M12-005_prompt_injection_robustness']['rate']}",
            f"- Traceability: {holdout['metrics']['M12-006_traceability']['rate']}",
            "",
            "## Baseline comparison (holdout)",
            "",
            f"- n: {paired['n']}",
            f"- ADAPT workflow score: {paired['adapt_score']}",
            f"- Single-prompt baseline score: {paired['baseline_score']}",
            f"- Absolute difference: {paired['absolute_difference']}",
            f"- Relative difference: {paired['relative_difference']}",
            f"- McNemar p-value: {paired['mcnemar']['p_value']}",
            f"- Statistically significant: {paired['statistically_significant']}",
            f"- Note: {paired['note']}",
            "",
        ]
    )
    return "\n".join(lines) + "\n"


def print_summary(payload: dict[str, Any]) -> None:
    meta = payload["meta"]
    print(f"Phase 12 backend={meta['backend']} selected={meta['selected_prompt_id']}")
    print(payload["report"])


def main() -> int:
    persist = "--no-persist" not in sys.argv
    live = "--live" in sys.argv
    payload = run_benchmark(persist=persist, live=live)
    print_summary(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
