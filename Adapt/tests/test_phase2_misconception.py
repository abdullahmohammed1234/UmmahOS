"""Misconception persistence, probing, and Phase 1F G-003 regressions."""

from __future__ import annotations

from adapt.models.enums import (
    AnswerStatus,
    ErrorPattern,
    EvidencePolarity,
    EvidenceReliability,
    EvidenceStrength,
    LearnerConfidence,
    LearningTrajectory,
    ReasoningQuality,
    StrategyName,
    Uncertainty,
)
from adapt.models.learner_state import MisconceptionRecord
from adapt.models.strategy import StrategyState
from benchmarks.phase1f.evaluator import run_adapt
from benchmarks.phase1f.scenarios import SCENARIO_BY_ID
from tests.helpers_phase2 import decide, make_evidence, make_state, phase2_pipeline


def test_first_misconception_flags_and_probes():
    state = make_state(
        pattern="CCCCW",
        mastery=0.72,
        trajectory=LearningTrajectory.REGRESSING,
        misconceptions=(MisconceptionRecord("DIST_PROP", 1, "SUSPECTED"),),
        error_pattern=ErrorPattern.CONCEPTUAL,
    )
    evidence = make_evidence(
        answer_status=AnswerStatus.INCORRECT,
        polarity=EvidencePolarity.NEGATIVE,
        reasoning_quality=ReasoningQuality.MODERATE,
        error_type=ErrorPattern.CONCEPTUAL,
        misconception_signal="DIST_PROP",
        evidence_strength=EvidenceStrength.MODERATE,
        evidence_reliability=EvidenceReliability.MODERATE,
        diagnostic_confidence=__import__("adapt.models.enums", fromlist=["DiagnosticConfidence"]).DiagnosticConfidence.MODERATE,
        confidence_signal=LearnerConfidence.HIGH,
    )
    decision = decide(
        state,
        evidence,
        strategy=StrategyState(current_strategy=StrategyName.INCREASE),
    )
    assert decision.decision == StrategyName.PROBE
    assert decision.strategy_state.misconception_flag == "FLAGGED"


def test_single_misconception_does_not_remediate():
    state = make_state(
        pattern="CCCCW",
        mastery=0.7,
        misconceptions=(MisconceptionRecord("DIST_PROP", 1, "SUSPECTED"),),
    )
    evidence = make_evidence(
        answer_status=AnswerStatus.INCORRECT,
        polarity=EvidencePolarity.NEGATIVE,
        misconception_signal="DIST_PROP",
        error_type=ErrorPattern.CONCEPTUAL,
        evidence_strength=EvidenceStrength.MODERATE,
    )
    decision = decide(state, evidence, strategy=StrategyState(current_strategy=StrategyName.MAINTAIN))
    assert decision.decision != StrategyName.REMEDIATE


def test_repeated_misconception_triggers_remediate():
    state = make_state(
        pattern="CCWWW",
        mastery=0.45,
        misconceptions=(MisconceptionRecord("DIST_PROP", 3, "REPEATED"),),
        error_pattern=ErrorPattern.CONCEPTUAL,
    )
    evidence = make_evidence(
        answer_status=AnswerStatus.INCORRECT,
        polarity=EvidencePolarity.NEGATIVE,
        misconception_signal="DIST_PROP",
        error_type=ErrorPattern.CONCEPTUAL,
        evidence_strength=EvidenceStrength.MODERATE,
    )
    decision = decide(state, evidence, strategy=StrategyState(current_strategy=StrategyName.PROBE))
    assert decision.decision == StrategyName.REMEDIATE


def test_clear_flag_when_misconception_does_not_repeat():
    state = make_state(pattern="CCCCWCCC", mastery=0.74)
    evidence = make_evidence()
    previous = StrategyState(
        current_strategy=StrategyName.PROBE,
        misconception_flag="FLAGGED",
        flagged_misconception_id="DIST_PROP",
    )
    decision = decide(state, evidence, strategy=previous)
    assert decision.decision != StrategyName.REMEDIATE
    assert decision.strategy_state.misconception_flag in {"CLEARED", None}


def test_g003_a_delayed_misconception_is_not_decrease():
    record = run_adapt(SCENARIO_BY_ID["G-003-A"], phase2_pipeline())
    strategy = record["decision_trace"]["strategy_decision"]["decision"]
    assert strategy in {"PROBE", "GATHER_EVIDENCE"}
    assert strategy != "DECREASE"


def test_g003_b_fractions_delayed_misconception_is_not_decrease():
    record = run_adapt(SCENARIO_BY_ID["G-003-B"], phase2_pipeline())
    strategy = record["decision_trace"]["strategy_decision"]["decision"]
    assert strategy in {"PROBE", "GATHER_EVIDENCE"}
    assert strategy != "DECREASE"


def test_g003_not_unconditional_new_misconception_equals_probe():
    weak = make_state(
        pattern="WWW",
        mastery=0.28,
        trajectory=LearningTrajectory.REGRESSING,
        uncertainty=Uncertainty.MODERATE_UNCERTAINTY,
        misconceptions=(MisconceptionRecord("DIST_PROP", 1, "SUSPECTED"),),
        error_pattern=ErrorPattern.CONCEPTUAL,
        reasoning=ReasoningQuality.WEAK,
    )
    evidence = make_evidence(
        answer_status=AnswerStatus.INCORRECT,
        polarity=EvidencePolarity.NEGATIVE,
        misconception_signal="DIST_PROP",
        error_type=ErrorPattern.CONCEPTUAL,
        reasoning_quality=ReasoningQuality.WEAK,
        confidence_signal=LearnerConfidence.LOW,
        evidence_strength=EvidenceStrength.MODERATE,
    )
    decision = decide(weak, evidence, strategy=StrategyState(current_strategy=StrategyName.MAINTAIN))
    assert decision.decision in {StrategyName.DECREASE, StrategyName.REMEDIATE, StrategyName.GATHER_EVIDENCE, StrategyName.PROBE}


def test_persistent_threshold_is_configurable():
    from adapt.strategy.config import StrategyConfig
    from adapt.strategy.engine import AdaptiveStrategyEngine

    state = make_state(
        pattern="CCWW",
        misconceptions=(MisconceptionRecord("DIST_PROP", 2, "SUSPECTED"),),
    )
    evidence = make_evidence(
        answer_status=AnswerStatus.INCORRECT,
        polarity=EvidencePolarity.NEGATIVE,
        misconception_signal="DIST_PROP",
        error_type=ErrorPattern.CONCEPTUAL,
        evidence_strength=EvidenceStrength.MODERATE,
    )
    early = AdaptiveStrategyEngine(StrategyConfig(misconception_remediate_threshold=2))
    late = AdaptiveStrategyEngine(StrategyConfig(misconception_remediate_threshold=4))
    assert decide(state, evidence, strategy=StrategyState(current_strategy=StrategyName.PROBE), engine=early).decision == StrategyName.REMEDIATE
    assert decide(state, evidence, strategy=StrategyState(current_strategy=StrategyName.PROBE), engine=late).decision != StrategyName.REMEDIATE
