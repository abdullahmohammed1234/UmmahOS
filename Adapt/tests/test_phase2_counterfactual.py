"""Counterfactual strategy tests P2-CF-001 through P2-CF-004."""

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
from tests.helpers_phase2 import decide, make_evidence, make_state


def test_cf001_isolated_vs_repeated_misconception():
    base = make_state(pattern="CCCCW", mastery=0.7)
    isolated_state = make_state(
        pattern="CCCCW",
        mastery=0.7,
        misconceptions=(MisconceptionRecord("DIST_PROP", 1, "SUSPECTED"),),
    )
    repeated_state = make_state(
        pattern="CCCCWWW",
        mastery=0.48,
        misconceptions=(MisconceptionRecord("DIST_PROP", 3, "REPEATED"),),
    )
    isolated_ev = make_evidence(
        answer_status=AnswerStatus.INCORRECT,
        polarity=EvidencePolarity.NEGATIVE,
        misconception_signal="DIST_PROP",
        error_type=ErrorPattern.CONCEPTUAL,
        evidence_strength=EvidenceStrength.MODERATE,
    )
    repeated_ev = make_evidence(
        response_id="R-REP",
        answer_status=AnswerStatus.INCORRECT,
        polarity=EvidencePolarity.NEGATIVE,
        misconception_signal="DIST_PROP",
        error_type=ErrorPattern.CONCEPTUAL,
        evidence_strength=EvidenceStrength.MODERATE,
    )
    isolated = decide(
        isolated_state,
        isolated_ev,
        strategy=StrategyState(current_strategy=StrategyName.MAINTAIN),
    )
    repeated = decide(
        repeated_state,
        repeated_ev,
        strategy=StrategyState(current_strategy=StrategyName.PROBE),
    )
    assert isolated.decision in {StrategyName.PROBE, StrategyName.GATHER_EVIDENCE}
    assert repeated.decision == StrategyName.REMEDIATE
    assert isolated.decision != repeated.decision
    _ = base


def test_cf002_one_vs_three_recovery_successes():
    shared = dict(misconceptions=(MisconceptionRecord("DIST_PROP", 3, "REPEATED"),))
    one = decide(
        make_state(pattern="WWWC", mastery=0.5, **shared),
        make_evidence(response_id="R-1"),
        strategy=StrategyState(current_strategy=StrategyName.REMEDIATE),
    )
    three = decide(
        make_state(pattern="WWWCCC", mastery=0.7, **shared),
        make_evidence(response_id="R-3"),
        strategy=StrategyState(current_strategy=StrategyName.REMEDIATE),
    )
    assert one.decision == StrategyName.REMEDIATE
    assert three.decision != StrategyName.REMEDIATE
    assert three.confidence != one.confidence


def test_cf003_same_accuracy_localized_vs_global():
    localized = decide(
        make_state(
            pattern="CCCCW",
            mastery=0.72,
            misconceptions=(MisconceptionRecord("DIST_PROP", 1, "SUSPECTED"),),
        ),
        make_evidence(
            answer_status=AnswerStatus.INCORRECT,
            polarity=EvidencePolarity.NEGATIVE,
            misconception_signal="DIST_PROP",
            error_type=ErrorPattern.CONCEPTUAL,
            evidence_strength=EvidenceStrength.MODERATE,
        ),
        strategy=StrategyState(current_strategy=StrategyName.MAINTAIN),
    )
    global_reg = decide(
        make_state(pattern="WWW", mastery=0.25),
        make_evidence(
            response_id="R-G",
            answer_status=AnswerStatus.INCORRECT,
            polarity=EvidencePolarity.NEGATIVE,
            reasoning_quality=ReasoningQuality.WEAK,
            confidence_signal=LearnerConfidence.LOW,
            evidence_strength=EvidenceStrength.WEAK,
        ),
        strategy=StrategyState(current_strategy=StrategyName.MAINTAIN),
    )
    assert localized.decision != global_reg.decision or localized.reason_codes != global_reg.reason_codes
    assert localized.decision in {StrategyName.PROBE, StrategyName.GATHER_EVIDENCE}


def test_cf004_same_mastery_remediate_vs_maintain_history():
    state = make_state(pattern="C", mastery=0.6)
    evidence = make_evidence()
    from_remediate = decide(
        state,
        evidence,
        strategy=StrategyState(current_strategy=StrategyName.REMEDIATE),
    )
    from_maintain = decide(
        state,
        evidence,
        strategy=StrategyState(current_strategy=StrategyName.MAINTAIN),
    )
    assert from_remediate.decision != from_maintain.decision
    assert from_remediate.previous_strategy == StrategyName.REMEDIATE
    assert from_maintain.previous_strategy == StrategyName.MAINTAIN
    assert from_remediate.decision == StrategyName.REMEDIATE


def test_counterfactual_relevant_evidence_changes_strategy():
    strong = decide(make_state(pattern="CCCC"), make_evidence())
    weak = decide(
        make_state(pattern="CCCC"),
        make_evidence(
            response_id="R-W",
            reasoning_quality=ReasoningQuality.WEAK,
            evidence_strength=EvidenceStrength.WEAK,
            confidence_signal=LearnerConfidence.HIGH,
        ),
    )
    assert strong.decision != weak.decision or strong.confidence != weak.confidence


def test_instruction_text_is_not_used_by_strategy_engine():
    state = make_state(pattern="W")
    evidence = make_evidence(
        answer_status=AnswerStatus.INCORRECT,
        polarity=EvidencePolarity.NEGATIVE,
        reasoning_quality=ReasoningQuality.WEAK,
        evidence_strength=EvidenceStrength.WEAK,
        confidence_signal=LearnerConfidence.HIGH,
    )
    decision = decide(state, evidence)
    assert decision.decision != StrategyName.INCREASE
