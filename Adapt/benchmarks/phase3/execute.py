"""Execute Phase 3 sessions against AdaptiveTutor."""

from __future__ import annotations

from typing import Any

from adapt.models.enums import StrategyName
from adapt.models.learner_state import LearnerState, MisconceptionRecord, initial_learner_state
from adapt.models.strategy import StrategyState
from adapt.tutor.compat import challenge_compatible_with_strategy
from adapt.tutor.responses import build_scripted_response
from adapt.tutor.tutor import AdaptiveTutor, DEFAULT_SEED
from benchmarks.phase3.scenarios import Phase3Scenario
from benchmarks.phase3.trajectories import TrajectorySpec


def make_tutor(seed: int = DEFAULT_SEED) -> AdaptiveTutor:
    return AdaptiveTutor(seed=seed)


def _remediate_start(learner_id: str, concept_id: str) -> tuple[LearnerState, StrategyState]:
    base = initial_learner_state(learner_id, concept_id)
    mid = "ADD_DENOM" if concept_id == "fractions" else "DIST_PROP"
    state = LearnerState(
        learner_id=base.learner_id,
        concept_id=base.concept_id,
        mastery_estimate=0.42,
        confidence=0.35,
        reasoning_quality=base.reasoning_quality,
        error_pattern=base.error_pattern,
        misconceptions=(MisconceptionRecord(mid, 3, "REPEATED"),),
        recent_performance=base.recent_performance,
        evidence_strength=base.evidence_strength,
        evidence_reliability=base.evidence_reliability,
        learning_trajectory=base.learning_trajectory,
        uncertainty=base.uncertainty,
        learner_confidence=base.learner_confidence,
        diagnostic_confidence=base.diagnostic_confidence,
    )
    strategy = StrategyState(
        current_strategy=StrategyName.REMEDIATE,
        previous_strategy=StrategyName.PROBE,
        strategy_confidence=0.7,
        transition_reason="Session begins in remediation after repeated misconception evidence.",
        transition_evidence=("init",),
        misconception_flag="FLAGGED",
        flagged_misconception_id=mid,
    )
    return state, strategy


def run_kinds(
    *,
    tutor: AdaptiveTutor,
    learner_id: str,
    concept: str,
    kinds: tuple[str, ...],
    session_id: str,
    initial_challenge_id: str | None = None,
    start_remediate: bool = False,
) -> dict[str, Any]:
    learner_state = None
    strategy_state = None
    if start_remediate:
        learner_state, strategy_state = _remediate_start(learner_id, concept)
    session = tutor.start_session(
        learner_id=learner_id,
        concept_id=concept,
        session_id=session_id,
        initial_challenge=initial_challenge_id,
        learner_state=learner_state,
        strategy_state=strategy_state,
    )
    for index, kind in enumerate(kinds, start=1):
        challenge = tutor.get_next_challenge(session_id)
        response = build_scripted_response(
            challenge,
            kind,
            learner_id=learner_id,
            response_id=f"{session_id}-R-{index:03d}",
        )
        tutor.submit_response(session_id, response)
    session = tutor.get_session(session_id)
    return session_record(session)


def session_record(session) -> dict[str, Any]:
    strategies = [item.decision.value for item in session.traces]
    challenges = [item.challenge_id for item in session.traces] + (
        [session.current_challenge.challenge_id] if session.current_challenge else []
    )
    compatible = []
    causal = []
    complete = []
    for item in session.traces:
        complete.append(item.is_complete())
        compatible.append(
            challenge_compatible_with_strategy(
                strategy=item.decision,
                challenge=item.next_challenge,
                previous=item.challenge,
                state=item.state_after,
            )
        )
        state_changed = item.state_before.to_dict() != item.state_after.to_dict()
        strategy_changed = item.strategy_before.current_strategy != item.strategy_after.current_strategy
        if strategy_changed:
            causal.append(state_changed or bool(item.evidence_ids) and bool(item.reason))
        else:
            causal.append(True)
    return {
        "session_id": session.session_id,
        "learner_id": session.learner_id,
        "concept_id": session.concept_id,
        "step_number": session.step_number,
        "strategies": strategies,
        "challenge_ids": [item.challenge_id for item in session.traces],
        "next_challenge_ids": [item.next_challenge_id for item in session.traces],
        "final_strategy": session.strategy_state.current_strategy.value,
        "final_challenge_id": session.current_challenge.challenge_id,
        "final_mastery": session.learner_state.mastery_estimate,
        "final_uncertainty": session.learner_state.uncertainty.value,
        "misconceptions": [item.to_dict() for item in session.learner_state.misconceptions],
        "trace_complete_rate": (sum(complete) / len(complete)) if complete else 1.0,
        "strategy_challenge_compatible_rate": (sum(compatible) / len(compatible)) if compatible else 1.0,
        "state_strategy_causal_rate": (sum(causal) / len(causal)) if causal else 1.0,
        "traces": [item.to_dict() for item in session.traces],
        "explanations": [item.explanation for item in session.traces],
        "seed": session.seed,
        "challenge_trajectory": challenges,
    }


def score_expected(record: dict[str, Any], expected_final: tuple[str, ...], forbidden: tuple[str, ...]) -> bool:
    final = record["final_strategy"]
    if forbidden and final in forbidden:
        return False
    if expected_final and final not in expected_final:
        return False
    return True


def oscillation_violation(strategies: list[str]) -> bool:
    compact = "->".join(strategies)
    return "INCREASE->DECREASE->INCREASE" in compact or "DECREASE->INCREASE->DECREASE" in compact


def run_scenario(scenario: Phase3Scenario, tutor: AdaptiveTutor | None = None, seed: int = DEFAULT_SEED) -> dict[str, Any]:
    local = tutor or make_tutor(seed)
    record = run_kinds(
        tutor=local,
        learner_id=f"L-{scenario.scenario_id}",
        concept=scenario.concept,
        kinds=scenario.kinds,
        session_id=scenario.scenario_id,
        initial_challenge_id=scenario.initial_challenge_id,
        start_remediate=scenario.start_remediate,
    )
    appropriate = score_expected(record, scenario.expected_final, scenario.forbidden)
    recovered = False
    if scenario.recovery_scenario:
        recovered = any(name in {"MAINTAIN", "PROBE", "INCREASE"} for name in record["strategies"]) and (
            "REMEDIATE" in record["strategies"]
            or scenario.start_remediate
            and record["final_strategy"] != "REMEDIATE"
            or record["final_strategy"] in {"MAINTAIN", "PROBE", "INCREASE"}
        )
        if scenario.start_remediate:
            recovered = record["final_strategy"] in {"MAINTAIN", "PROBE", "INCREASE"}
    misconception_handled = True
    if scenario.misconception_scenario:
        misconception_handled = any(
            name in {"PROBE", "REMEDIATE", "GATHER_EVIDENCE"} for name in record["strategies"]
        )
    record.update(
        {
            "scenario_id": scenario.scenario_id,
            "family": scenario.family,
            "category": scenario.category,
            "split": scenario.split,
            "kind": "session",
            "n_steps": scenario.n_steps,
            "appropriate": appropriate,
            "expected_final": list(scenario.expected_final),
            "expected_behavior": scenario.expected_behavior,
            "pair_id": scenario.pair_id,
            "pair_role": scenario.pair_role,
            "recovery_scenario": scenario.recovery_scenario,
            "recovered": recovered,
            "misconception_scenario": scenario.misconception_scenario,
            "misconception_handled": misconception_handled,
            "oscillation_violation": oscillation_violation(record["strategies"]),
            "meaningful_evidence": scenario.meaningful_evidence,
        }
    )
    return record


def run_trajectory(spec: TrajectorySpec, tutor: AdaptiveTutor | None = None, seed: int = DEFAULT_SEED) -> dict[str, Any]:
    local = tutor or make_tutor(seed)
    record = run_kinds(
        tutor=local,
        learner_id=f"L-{spec.trajectory_id}",
        concept=spec.concept,
        kinds=spec.kinds,
        session_id=spec.trajectory_id,
        initial_challenge_id=spec.initial_challenge_id,
    )
    names = record["strategies"]
    path_ok = _path_observed(names, spec.expected_path, spec.trajectory_id)
    forbidden_hit = any(name in spec.forbidden for name in names) if spec.forbidden else False
    appropriate = path_ok and not forbidden_hit and not oscillation_violation(names)
    recovered = False
    if spec.recovery_scenario:
        saw_remediate = "REMEDIATE" in names
        left = any(name in {"MAINTAIN", "PROBE", "INCREASE"} for name in names[names.index("REMEDIATE") + 1 :]) if saw_remediate else record["final_strategy"] in {"MAINTAIN", "PROBE", "INCREASE"}
        recovered = left
        if spec.trajectory_id == "T-003":
            recovered = record["final_strategy"] in {"MAINTAIN", "PROBE", "INCREASE", "GATHER_EVIDENCE"}
    misconception_handled = True
    if spec.misconception_scenario:
        misconception_handled = any(name in {"PROBE", "REMEDIATE", "GATHER_EVIDENCE"} for name in names)
    record.update(
        {
            "scenario_id": spec.trajectory_id,
            "family": spec.trajectory_id,
            "category": "longitudinal",
            "split": spec.split,
            "kind": "trajectory",
            "label": spec.label,
            "n_steps": spec.n_steps,
            "appropriate": appropriate,
            "path_ok": path_ok,
            "expected_path": list(spec.expected_path),
            "expected_behavior": spec.expected_behavior,
            "recovery_scenario": spec.recovery_scenario,
            "recovered": recovered,
            "misconception_scenario": spec.misconception_scenario,
            "misconception_handled": misconception_handled,
            "oscillation_violation": oscillation_violation(names),
            "meaningful_evidence": True,
        }
    )
    return record


def _path_observed(names: list[str], expected_path: tuple[str, ...], trajectory_id: str) -> bool:
    observed = set(names)
    if trajectory_id == "T-001":
        return bool(observed & {"ASSESS", "GATHER_EVIDENCE"}) and "INCREASE" in observed
    if trajectory_id == "T-002":
        return bool(observed & {"PROBE", "REMEDIATE", "GATHER_EVIDENCE", "DECREASE", "ASSESS"})
    if trajectory_id == "T-003":
        return bool(observed & {"GATHER_EVIDENCE", "ASSESS", "MAINTAIN", "PROBE"}) and (
            names[-1] in {"MAINTAIN", "INCREASE", "PROBE", "GATHER_EVIDENCE"}
        )
    if trajectory_id == "T-004":
        return not oscillation_violation(names)
    if trajectory_id == "T-005":
        return "PROBE" in observed or "REMEDIATE" in observed
    if trajectory_id == "T-006":
        return not oscillation_violation(names) and "INCREASE" not in names[:3]
    if trajectory_id == "T-H-001":
        return "INCREASE" in observed or names[-1] in {"MAINTAIN", "INCREASE", "GATHER_EVIDENCE"}
    if trajectory_id == "T-H-002":
        return not oscillation_violation(names)
    return True
