"""Phase 2 evaluator. Uses the strategy-enabled pipeline; does not touch Phase 1F."""

from __future__ import annotations

from typing import Any

from adapt.adaptation.challenge_selector import ChallengeSelector
from adapt.models.enums import StrategyName
from adapt.models.learner_state import initial_learner_state
from adapt.pipeline import AdaptPipeline
from adapt.strategy.engine import AdaptiveStrategyEngine
from benchmarks.phase1f.challenge_bank import COMBINED_BANK, get_challenge
from benchmarks.phase2.scenarios import Scenario, scenario_steps


def make_pipeline() -> AdaptPipeline:
    return AdaptPipeline(
        selector=ChallengeSelector(bank=COMBINED_BANK),
        strategy_engine=AdaptiveStrategyEngine(),
    )


def _traceable(record: dict[str, Any]) -> bool:
    decision = record.get("strategy_decision") or {}
    return bool(
        decision.get("decision")
        and decision.get("reason")
        and decision.get("evidence_ids")
        and decision.get("state_snapshot") is not None
        and decision.get("confidence") is not None
        and decision.get("transition")
    )


def _unnecessary(traces) -> bool:
    names = [item.strategy_decision.decision.value for item in traces if item.strategy_decision]
    compact = "->".join(names)
    if "INCREASE->DECREASE->INCREASE" in compact:
        return True
    if "DECREASE->INCREASE->DECREASE" in compact:
        return True
    return False


def _recovery(scenario: Scenario, traces) -> tuple[bool, int | None]:
    if not scenario.recovery_scenario:
        return False, None
    entered = False
    successes = 0
    recovered = False
    latency = None
    for trace in traces:
        strategy = trace.strategy_decision.decision if trace.strategy_decision else None
        if strategy == StrategyName.REMEDIATE:
            entered = True
            if trace.evidence.answer_status.value == "CORRECT":
                successes += 1
            else:
                successes = 0
        elif entered and strategy in {StrategyName.MAINTAIN, StrategyName.PROBE, StrategyName.INCREASE}:
            recovered = True
            extra = 1 if trace.evidence.answer_status.value == "CORRECT" else 0
            latency = successes + extra
            break
    if not entered:
        last = traces[-1].strategy_decision.decision if traces[-1].strategy_decision else None
        recovered = last in {StrategyName.MAINTAIN, StrategyName.PROBE, StrategyName.INCREASE}
        latency = 3 if recovered else None
    return recovered, latency


def score_decision(scenario: Scenario, traces) -> dict[str, Any]:
    last = traces[-1]
    strategy = last.strategy_decision.decision.value if last.strategy_decision else "MISSING"
    appropriate = strategy in scenario.expected_strategies
    if strategy in scenario.forbidden_strategies:
        appropriate = False
    recovered, latency = _recovery(scenario, traces)
    record = {
        "scenario_id": scenario.scenario_id,
        "family": scenario.family,
        "concept": scenario.concept,
        "category": scenario.category,
        "variant": scenario.variant,
        "strategy": strategy,
        "adaptation_action": last.adaptation_decision.decision.value,
        "expected_strategies": list(scenario.expected_strategies),
        "expected_behavior": scenario.expected_behavior,
        "appropriate": appropriate,
        "evidence": last.evidence.to_dict(),
        "state_before": last.learner_state_before.to_dict(),
        "state_after": last.learner_state_after.to_dict(),
        "strategy_decision": None if last.strategy_decision is None else last.strategy_decision.to_dict(),
        "strategy_state": None if last.strategy_state is None else last.strategy_state.to_dict(),
        "decision_trace": last.to_dict(),
        "next_challenge_id": last.next_challenge.challenge_id,
        "recovery_scenario": scenario.recovery_scenario,
        "recovered_strategy": recovered,
        "recovery_latency": latency,
        "regression_scenario": scenario.regression_scenario,
        "misconception_scenario": scenario.misconception_scenario,
        "stability_scenario": scenario.stability_scenario,
        "unnecessary_transition": _unnecessary(traces),
        "strategy_path": [
            item.strategy_decision.decision.value for item in traces if item.strategy_decision
        ],
        "mastery_path": [round(item.learner_state_after.mastery_estimate, 4) for item in traces],
    }
    record["traceable"] = _traceable(record)
    if not record["traceable"]:
        record["appropriate"] = False
    if scenario.family == "P2-001":
        record["separated"] = strategy in {"PROBE", "GATHER_EVIDENCE"} and strategy != "DECREASE"
    elif scenario.family == "P2-002":
        record["separated"] = strategy in {"DECREASE", "GATHER_EVIDENCE"}
    else:
        record["separated"] = None
    return record


def run_scenario(scenario: Scenario, pipeline: AdaptPipeline | None = None) -> dict[str, Any]:
    pipe = pipeline or make_pipeline()
    learner_id = f"p2-{scenario.scenario_id}"
    steps = scenario_steps(scenario, learner_id)
    concept = get_challenge(scenario.current_challenge_id).concept_id
    traces = pipe.run_sequence(
        learner_state=initial_learner_state(learner_id, concept),
        steps=steps,
    )
    return score_decision(scenario, traces)


def evaluate_scenarios(scenarios: tuple[Scenario, ...], pipeline: AdaptPipeline | None = None) -> list[dict[str, Any]]:
    pipe = pipeline or make_pipeline()
    return [run_scenario(item, pipe) for item in scenarios]
