"""Strategy recovery is distinct from state (mastery) recovery. Includes G-005-D."""

from __future__ import annotations

from adapt.models.enums import (
    AnswerStatus,
    ErrorPattern,
    EvidencePolarity,
    EvidenceStrength,
    LearnerConfidence,
    ReasoningQuality,
    StrategyName,
)
from adapt.models.learner_state import MisconceptionRecord
from adapt.models.strategy import StrategyState
from benchmarks.phase1f.evaluator import run_adapt
from benchmarks.phase1f.scenarios import SCENARIO_BY_ID
from tests.helpers_phase2 import decide, make_evidence, make_state, phase2_pipeline


def test_g005_d_strategy_recovers_after_successful_remediation():
    record = run_adapt(SCENARIO_BY_ID["G-005-D"], phase2_pipeline())
    strategy = record["decision_trace"]["strategy_decision"]["decision"]
    mastery_path = record["mastery_path"]
    assert mastery_path[-1] > mastery_path[2]
    assert strategy in {"MAINTAIN", "PROBE", "INCREASE"}
    assert strategy != "REMEDIATE"


def test_g005_a_algebra_recovery_also_leaves_remediate():
    record = run_adapt(SCENARIO_BY_ID["G-005-A"], phase2_pipeline())
    strategy = record["decision_trace"]["strategy_decision"]["decision"]
    assert strategy != "REMEDIATE"


def test_state_recovery_is_not_automatically_strategy_recovery():
    state = make_state(
        pattern="WWWC",
        mastery=0.55,
        misconceptions=(MisconceptionRecord("DIST_PROP", 3, "REPEATED"),),
    )
    evidence = make_evidence()
    decision = decide(
        state,
        evidence,
        strategy=StrategyState(current_strategy=StrategyName.REMEDIATE),
    )
    assert state.mastery_estimate >= 0.5
    assert decision.decision == StrategyName.REMEDIATE


def test_three_strong_successes_recover_with_higher_confidence_than_one():
    shared = dict(
        misconceptions=(MisconceptionRecord("DIST_PROP", 3, "REPEATED"),),
    )
    one = decide(
        make_state(pattern="WWWC", mastery=0.52, **shared),
        make_evidence(),
        strategy=StrategyState(current_strategy=StrategyName.REMEDIATE),
    )
    three = decide(
        make_state(pattern="WWWCCC", mastery=0.7, **shared),
        make_evidence(),
        strategy=StrategyState(current_strategy=StrategyName.REMEDIATE),
    )
    assert one.decision == StrategyName.REMEDIATE
    assert three.decision != StrategyName.REMEDIATE
    assert three.confidence > one.confidence


def test_recovery_requires_strong_reasoning_not_correctness_alone():
    state = make_state(
        pattern="WWWCCC",
        mastery=0.68,
        misconceptions=(MisconceptionRecord("DIST_PROP", 3, "REPEATED"),),
        reasoning=ReasoningQuality.WEAK,
    )
    evidence = make_evidence(
        reasoning_quality=ReasoningQuality.WEAK,
        evidence_strength=EvidenceStrength.WEAK,
        confidence_signal=LearnerConfidence.HIGH,
    )
    decision = decide(
        state,
        evidence,
        strategy=StrategyState(current_strategy=StrategyName.REMEDIATE),
    )
    assert decision.decision == StrategyName.REMEDIATE


def test_failed_remediation_stays_in_remediate():
    state = make_state(
        pattern="WWWWW",
        mastery=0.25,
        misconceptions=(MisconceptionRecord("DIST_PROP", 5, "REPEATED"),),
        error_pattern=ErrorPattern.CONCEPTUAL,
    )
    evidence = make_evidence(
        answer_status=AnswerStatus.INCORRECT,
        polarity=EvidencePolarity.NEGATIVE,
        misconception_signal="DIST_PROP",
        error_type=ErrorPattern.CONCEPTUAL,
        evidence_strength=EvidenceStrength.MODERATE,
    )
    decision = decide(
        state,
        evidence,
        strategy=StrategyState(current_strategy=StrategyName.REMEDIATE),
    )
    assert decision.decision == StrategyName.REMEDIATE


def test_recovery_does_not_require_concept_name():
    state = make_state(
        pattern="WWWCCC",
        mastery=0.7,
        concept_id="fractions",
        misconceptions=(MisconceptionRecord("ADD_DENOM", 3, "REPEATED"),),
    )
    evidence = make_evidence()
    decision = decide(
        state,
        evidence,
        strategy=StrategyState(current_strategy=StrategyName.REMEDIATE),
    )
    assert decision.decision in {StrategyName.MAINTAIN, StrategyName.PROBE}


def test_remediation_does_not_persist_without_justification_after_strong_recovery():
    state = make_state(
        pattern="WWWCCC",
        mastery=0.72,
        misconceptions=(MisconceptionRecord("DIST_PROP", 3, "RESOLVED"),),
    )
    evidence = make_evidence()
    decision = decide(
        state,
        evidence,
        strategy=StrategyState(current_strategy=StrategyName.REMEDIATE),
    )
    assert decision.decision != StrategyName.REMEDIATE
