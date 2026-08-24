"""Phase 1F evaluator. Uses Phase 1D pipeline with an extended bank; does not modify Phase 1E."""

from __future__ import annotations

from typing import Any

from adapt.adaptation.challenge_selector import ChallengeSelector
from adapt.models.learner_state import initial_learner_state
from adapt.pipeline import AdaptPipeline
from benchmarks.phase1e.normalization import normalize_decision
from benchmarks.phase1f.challenge_bank import COMBINED_BANK, get_challenge
from benchmarks.phase1f.scenarios import Scenario, scenario_steps


def make_pipeline() -> AdaptPipeline:
    return AdaptPipeline(selector=ChallengeSelector(bank=COMBINED_BANK))


def _traceable(record: dict[str, Any]) -> bool:
    decision = record.get("decision_object") or {}
    return bool(
        decision.get("reason")
        and decision.get("evidence_used")
        and decision.get("confidence")
        and record.get("state_after")
    )


def _failure_type(scenario: Scenario, decision: str, appropriate: bool) -> str | None:
    if appropriate:
        return None
    if decision == "INCREASE_DIFFICULTY" and scenario.family in {"G-007", "G-009", "G-015"}:
        return "UNCERTAINTY_FAILURE"
    if decision == "REMEDIATE" and scenario.family in {"G-002", "G-004", "G-010"}:
        return "OBSERVATION_FAILURE"
    if decision == "REMEDIATE" and scenario.family == "G-005":
        return "RECOVERY_FAILURE"
    if scenario.family == "G-006":
        return "ADAPTATION_FAILURE"
    if scenario.family == "G-003":
        return "MISCONCEPTION_PERSISTENCE"
    if scenario.family == "G-001":
        return "GENERALIZATION_FAILURE"
    if scenario.family == "G-015":
        return "DECISION_FAILURE"
    return "GENERALIZATION_FAILURE"


def _severity(scenario: Scenario, appropriate: bool) -> str | None:
    if appropriate:
        return None
    if scenario.family in {"G-005", "G-015", "G-007", "G-009"}:
        return "HIGH"
    if scenario.family in {"G-003", "G-006", "G-011", "G-012"}:
        return "MEDIUM"
    return "LOW"


def score_decision(
    scenario: Scenario,
    *,
    decision_raw: object,
    evidence: dict[str, Any] | None,
    state_before: dict[str, Any] | None,
    state_after: dict[str, Any] | None,
    decision_object: dict[str, Any] | None,
    extras: dict[str, Any] | None = None,
) -> dict[str, Any]:
    decision = normalize_decision(decision_raw)
    appropriate = decision in scenario.expected_decisions
    if decision in scenario.forbidden_decisions:
        appropriate = False
    if (
        scenario.require_not_error_type
        and evidence
        and evidence.get("error_type") == scenario.require_not_error_type
    ):
        appropriate = False
    record = {
        "scenario_id": scenario.scenario_id,
        "split": scenario.split,
        "category": scenario.category,
        "family": scenario.family,
        "system": "ADAPT",
        "decision": decision,
        "expected_behavior": scenario.expected_adaptive_behavior,
        "expected_decisions": list(scenario.expected_decisions),
        "appropriate": appropriate,
        "evidence": evidence,
        "state_before": state_before,
        "state_after": state_after,
        "decision_object": decision_object,
        "failure_type": _failure_type(scenario, decision, appropriate),
        "severity": _severity(scenario, appropriate),
        "recovery_scenario": scenario.recovery_scenario,
        "persistence_scenario": scenario.persistence_scenario,
        "novel": scenario.novel,
        "multi_dimension": scenario.multi_dimension,
        "concept": scenario.concept,
        "variant": scenario.variant,
        **(extras or {}),
    }
    record["traceable"] = _traceable(record)
    if not record["traceable"]:
        record["appropriate"] = False
        record["failure_type"] = record["failure_type"] or "DECISION_FAILURE"
        record["severity"] = "HIGH"
    return record


def run_adapt(scenario: Scenario, pipeline: AdaptPipeline | None = None) -> dict[str, Any]:
    pipe = pipeline or make_pipeline()
    learner_id = f"1f-{scenario.scenario_id}"
    steps = scenario_steps(scenario, learner_id)
    concept = get_challenge(scenario.current_challenge_id).concept_id
    traces = pipe.run_sequence(
        learner_state=initial_learner_state(learner_id, concept),
        steps=steps,
    )
    last = traces[-1]
    mastery_path = [round(item.learner_state_after.mastery_estimate, 4) for item in traces]
    recovered = False
    if scenario.recovery_scenario and len(traces) >= 4:
        after_fail = traces[2].learner_state_after.mastery_estimate
        recovered = last.learner_state_after.mastery_estimate > after_fail + 0.02
        active = [
            item
            for item in last.learner_state_after.misconceptions
            if item.status != "RESOLVED"
        ]
        resolved = not active
        recovered = recovered or resolved
    persisted = False
    if scenario.recovery_scenario:
        active = [
            item
            for item in last.learner_state_after.misconceptions
            if item.status != "RESOLVED"
        ]
        persisted = bool(active) and last.adaptation_decision.decision.value == "REMEDIATE"
    strategy_stalled = False
    if scenario.persistence_scenario:
        strategy_stalled = last.adaptation_decision.decision.value not in {
            "REMEDIATE",
            "CHANGE_REPRESENTATION",
            "GATHER_MORE_EVIDENCE",
            "DECREASE_DIFFICULTY",
        }
    extras = {
        "decision_trace": last.to_dict(),
        "next_challenge_id": last.next_challenge.challenge_id,
        "mastery_path": mastery_path,
        "recovered": recovered,
        "misconception_persisted": persisted,
        "strategy_stalled": strategy_stalled,
        "step_count": len(traces),
        "trajectory_id": None,
        "step": len(traces),
    }
    return score_decision(
        scenario,
        decision_raw=last.adaptation_decision.decision,
        evidence=last.evidence.to_dict(),
        state_before=last.learner_state_before.to_dict(),
        state_after=last.learner_state_after.to_dict(),
        decision_object=last.adaptation_decision.to_dict(),
        extras=extras,
    )


def evaluate_scenarios(scenarios: tuple[Scenario, ...], pipeline: AdaptPipeline | None = None) -> list[dict[str, Any]]:
    pipe = pipeline or make_pipeline()
    return [run_adapt(item, pipe) for item in scenarios]
