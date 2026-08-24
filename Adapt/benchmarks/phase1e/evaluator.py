"""Evaluate ADAPT and the Phase 1E baseline on frozen scenarios."""

from __future__ import annotations

from typing import Any

from adapt.adaptation.challenge_bank import CONCEPT_ID
from adapt.models.learner_state import initial_learner_state
from adapt.pipeline import AdaptPipeline
from benchmarks.phase1e.baseline import BenchmarkBaseline
from benchmarks.phase1e.normalization import normalize_decision
from benchmarks.phase1e.scenarios import Scenario, counterfactual_pairs, scenario_steps


def _traceable(record: dict[str, Any], system: str) -> bool:
    if system != "ADAPT":
        return False
    decision = record.get("decision_object") or {}
    state = record.get("learner_state_after")
    reasons = decision.get("reason") if isinstance(decision, dict) else None
    evidence_used = decision.get("evidence_used") if isinstance(decision, dict) else None
    confidence = decision.get("confidence") if isinstance(decision, dict) else None
    return bool(reasons) and bool(evidence_used) and bool(confidence) and state is not None


def _classify_flags(scenario: Scenario, decision: str, appropriate: bool) -> dict[str, bool]:
    false_mastery = decision == "INCREASE_DIFFICULTY" and scenario.family in {
        "S-002",
        "S-003",
        "S-006",
    }
    uncertainty_overconfidence = decision == "INCREASE_DIFFICULTY" and scenario.family in {
        "S-002",
        "S-006",
        "S-007",
    }
    false_weakness = decision == "REMEDIATE" and scenario.family == "S-004"
    overreaction = (
        (decision == "DECREASE_DIFFICULTY" and scenario.family == "S-008")
        or (decision == "INCREASE_DIFFICULTY" and scenario.family == "S-009")
    )
    underreaction = (not appropriate) and scenario.family in {"S-001", "S-005"}
    misconception_persisted = scenario.family == "S-005" and decision not in {
        "REMEDIATE",
        "CHANGE_REPRESENTATION",
        "GATHER_MORE_EVIDENCE",
    }
    return {
        "false_mastery": false_mastery,
        "false_weakness": false_weakness,
        "overreaction": overreaction,
        "underreaction": underreaction,
        "uncertainty_overconfidence": uncertainty_overconfidence,
        "misconception_persisted": misconception_persisted,
    }


def _error_type(scenario: Scenario, decision: str, appropriate: bool, extra: str | None) -> str | None:
    if extra:
        return extra
    if appropriate:
        return None
    if decision == "INCREASE_DIFFICULTY" and scenario.family in {"S-002", "S-003"}:
        return "FALSE_MASTERY"
    if decision == "INCREASE_DIFFICULTY" and scenario.family in {"S-006", "S-007"}:
        return "UNCERTAINTY_OVERCONFIDENCE"
    if decision == "DECREASE_DIFFICULTY" and scenario.family == "S-008":
        return "OVERREACTION"
    if decision == "INCREASE_DIFFICULTY" and scenario.family == "S-009":
        return "OVERREACTION"
    if scenario.family == "S-005":
        return "MISSED_MISCONCEPTION"
    if scenario.family == "S-001":
        return "UNDERREACTION"
    if scenario.family == "S-004" and decision == "REMEDIATE":
        return "FALSE_WEAKNESS"
    return "OTHER"


def _difficulty_appropriate(scenario: Scenario, next_difficulty: str | None, decision: str) -> bool:
    if next_difficulty and next_difficulty in scenario.forbid_next_difficulty:
        return False
    if scenario.family == "S-008" and decision == "DECREASE_DIFFICULTY":
        return False
    if scenario.family == "S-001" and decision != "INCREASE_DIFFICULTY":
        return False
    if scenario.family == "S-005" and decision not in {
        "REMEDIATE",
        "CHANGE_REPRESENTATION",
        "GATHER_MORE_EVIDENCE",
    }:
        return False
    return True


def score_decision(
    scenario: Scenario,
    *,
    system: str,
    decision_raw: object,
    next_difficulty: str | None,
    evidence: dict[str, Any] | None,
    learner_state_before: dict[str, Any] | None,
    learner_state_after: dict[str, Any] | None,
    decision_object: dict[str, Any] | None,
    extras: dict[str, Any] | None = None,
) -> dict[str, Any]:
    decision = normalize_decision(decision_raw)
    extra_error = None
    appropriate = decision in scenario.expected_decisions
    if decision in scenario.forbidden_decisions:
        appropriate = False
    if (
        system == "ADAPT"
        and scenario.require_not_error_type
        and evidence
        and evidence.get("error_type") == scenario.require_not_error_type
    ):
        appropriate = False
        extra_error = "FALSE_WEAKNESS"
    if next_difficulty and next_difficulty in scenario.forbid_next_difficulty:
        appropriate = False
        if extra_error is None:
            extra_error = "OVERREACTION"

    flags = _classify_flags(scenario, decision, appropriate)
    noise_stable = not (scenario.family == "S-008" and decision == "DECREASE_DIFFICULTY")
    record = {
        "scenario_id": scenario.scenario_id,
        "family": scenario.family,
        "system": system,
        "decision": decision,
        "expected_behavior": scenario.expected_adaptive_behavior,
        "expected_decisions": list(scenario.expected_decisions),
        "appropriate": appropriate,
        "error_type": _error_type(scenario, decision, appropriate, extra_error),
        "learner_state_before": learner_state_before,
        "learner_state_after": learner_state_after,
        "evidence": evidence,
        "decision_object": decision_object,
        "next_difficulty": next_difficulty,
        "difficulty_appropriate": _difficulty_appropriate(scenario, next_difficulty, decision),
        "noise_stable": noise_stable if scenario.family == "S-008" else None,
        "variant": scenario.variant,
        "counterfactual_pair_id": scenario.counterfactual_pair_id,
        "counterfactual_role": scenario.counterfactual_role,
        "category": scenario.category,
        **flags,
        **(extras or {}),
    }
    record["traceable"] = _traceable(record, system)
    if system == "ADAPT" and not record["traceable"]:
        record["error_type"] = record["error_type"] or "UNTRACEABLE_DECISION"
        record["appropriate"] = False
    return record


def run_adapt(scenario: Scenario, pipeline: AdaptPipeline | None = None) -> dict[str, Any]:
    pipe = pipeline or AdaptPipeline()
    learner_id = f"adapt-{scenario.scenario_id}"
    steps = scenario_steps(scenario, learner_id)
    state = initial_learner_state(learner_id, CONCEPT_ID)
    traces = pipe.run_sequence(learner_state=state, steps=steps)
    last = traces[-1]
    return score_decision(
        scenario,
        system="ADAPT",
        decision_raw=last.adaptation_decision.decision,
        next_difficulty=last.next_challenge.difficulty.value,
        evidence=last.evidence.to_dict(),
        learner_state_before=last.learner_state_before.to_dict(),
        learner_state_after=last.learner_state_after.to_dict(),
        decision_object=last.adaptation_decision.to_dict(),
        extras={
            "decision_trace": last.to_dict(),
            "next_challenge_id": last.next_challenge.challenge_id,
            "next_challenge_type": last.next_challenge.challenge_type.value,
        },
    )


def run_baseline(scenario: Scenario, baseline: BenchmarkBaseline | None = None) -> dict[str, Any]:
    tutor = baseline or BenchmarkBaseline()
    learner_id = f"base-{scenario.scenario_id}"
    steps = scenario_steps(scenario, learner_id)
    history = steps[:-1]
    challenge, response = steps[-1]
    result = tutor.respond(challenge, response, history)
    return score_decision(
        scenario,
        system="BASELINE",
        decision_raw=result.decision,
        next_difficulty=result.next_challenge.difficulty.value,
        evidence=None,
        learner_state_before=None,
        learner_state_after=None,
        decision_object={
            "decision": result.decision,
            "reason": list(result.reasons),
            "diagnosis": result.diagnosis,
        },
        extras={
            "decision_trace": None,
            "baseline_diagnosis": result.diagnosis,
            "next_challenge_id": result.next_challenge.challenge_id,
            "next_challenge_type": result.next_challenge.challenge_type.value,
            "answer_status": result.answer_status,
        },
    )


def pair_counterfactuals(system_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {
        (item.get("counterfactual_pair_id"), item.get("counterfactual_role")): item
        for item in system_records
        if item.get("counterfactual_pair_id")
    }
    results = []
    for pair_id, members in counterfactual_pairs().items():
        rec_a = by_id.get((pair_id, "A"))
        rec_b = by_id.get((pair_id, "B"))
        if rec_a is None or rec_b is None:
            continue
        differentiated = rec_a["decision"] != rec_b["decision"]
        expected_different = True
        a_ok = rec_a["appropriate"] is True
        b_ok = rec_b["appropriate"] is True
        evidence_sensitive = differentiated and a_ok and b_ok
        results.append(
            {
                "pair_id": pair_id,
                "dimension": members["A"].counterfactual_dimension,
                "decision_a": rec_a["decision"],
                "decision_b": rec_b["decision"],
                "differentiated": differentiated,
                "expected_different": expected_different,
                "evidence_sensitive": evidence_sensitive,
                "appropriate_a": a_ok,
                "appropriate_b": b_ok,
            }
        )
    return results


def evaluate_suite(scenarios: tuple[Scenario, ...] | None = None) -> dict[str, Any]:
    from benchmarks.phase1e.scenarios import SCENARIOS

    suite = scenarios or SCENARIOS
    pipeline = AdaptPipeline()
    baseline = BenchmarkBaseline()
    adapt_records = [run_adapt(item, pipeline) for item in suite]
    baseline_records = [run_baseline(item, baseline) for item in suite]
    paired = []
    adapt_by_id = {item["scenario_id"]: item for item in adapt_records}
    base_by_id = {item["scenario_id"]: item for item in baseline_records}
    for scenario in suite:
        paired.append(
            {
                "scenario_id": scenario.scenario_id,
                "family": scenario.family,
                "adapt": adapt_by_id[scenario.scenario_id],
                "baseline": base_by_id[scenario.scenario_id],
            }
        )
    return {
        "adapt_records": adapt_records,
        "baseline_records": baseline_records,
        "paired": paired,
        "adapt_pairs": pair_counterfactuals(adapt_records),
        "baseline_pairs": pair_counterfactuals(baseline_records),
    }
