"""Phase 1D required tests 1–12 plus determinism, serialization, errors, and baseline."""

from __future__ import annotations

import json

import pytest

from adapt.adaptation.challenge_bank import DIST_PROP, get_challenge
from adapt.analysis.evidence_analyzer import EvidenceAnalyzer
from adapt.baseline.baseline_tutor import BaselineTutor, compare_sequence
from adapt.errors import (
    InvalidEvidenceError,
    InvalidLearnerStateError,
    MissingChallengeError,
)
from adapt.models.enums import (
    AdaptationAction,
    AnswerStatus,
    DiagnosticConfidence,
    Difficulty,
    ErrorPattern,
    EvidenceReliability,
    EvidenceStrength,
    LearnerConfidence,
    LearningTrajectory,
    ReasoningQuality,
    STRENGTH_RANK,
    Uncertainty,
)
from adapt.models.evidence import Evidence
from adapt.models.learner_state import LearnerState
from adapt.pipeline import AdaptPipeline
from adapt.state.state_updater import StateUpdater
from tests.helpers import (
    ARITHMETIC_REASONING,
    DIAGNOSTIC,
    GUESS_REASONING,
    MEDIUM,
    MISCONCEPTION_REASONING,
    STRONG_REASONING,
    WEAK_REASONING,
    make_response,
    new_state,
    run_one,
)


def test_01_lucky_guess_is_not_strong_mastery_evidence():
    response = make_response(
        response_id="R-001",
        challenge_id=MEDIUM.challenge_id,
        answer="4",
        reasoning=GUESS_REASONING,
        learner_confidence=LearnerConfidence.LOW,
    )
    trace = run_one(new_state(), MEDIUM, response)
    assert trace.evidence.answer_status == AnswerStatus.CORRECT
    assert trace.evidence.evidence_strength != EvidenceStrength.STRONG
    assert trace.evidence.evidence_strength in {
        EvidenceStrength.WEAK,
        EvidenceStrength.INSUFFICIENT,
    }
    assert trace.evidence.reasoning_quality == ReasoningQuality.WEAK
    delta = trace.learner_state_after.mastery_estimate - trace.learner_state_before.mastery_estimate
    assert delta < 0.05


def test_02_correct_strong_reasoning_is_strong_positive_evidence():
    response = make_response(
        response_id="R-002",
        challenge_id=MEDIUM.challenge_id,
        answer="4",
        reasoning=STRONG_REASONING,
        learner_confidence=LearnerConfidence.HIGH,
    )
    evidence = EvidenceAnalyzer().analyze(response, MEDIUM)
    assert evidence.answer_status == AnswerStatus.CORRECT
    assert evidence.reasoning_quality == ReasoningQuality.STRONG
    assert evidence.evidence_strength == EvidenceStrength.STRONG
    assert evidence.evidence_reliability == EvidenceReliability.HIGH


def test_03_correct_weak_reasoning_is_weaker_than_strong_reasoning():
    strong = EvidenceAnalyzer().analyze(
        make_response(
            response_id="R-002b",
            challenge_id=MEDIUM.challenge_id,
            answer="4",
            reasoning=STRONG_REASONING,
            learner_confidence=LearnerConfidence.HIGH,
        ),
        MEDIUM,
    )
    weak = EvidenceAnalyzer().analyze(
        make_response(
            response_id="R-003",
            challenge_id=MEDIUM.challenge_id,
            answer="4",
            reasoning=WEAK_REASONING,
            learner_confidence=LearnerConfidence.LOW,
        ),
        MEDIUM,
    )
    assert strong.answer_status == weak.answer_status == AnswerStatus.CORRECT
    assert STRENGTH_RANK[weak.evidence_strength] < STRENGTH_RANK[strong.evidence_strength]
    assert weak.evidence_strength in {EvidenceStrength.WEAK, EvidenceStrength.MODERATE}


def test_04_wrong_answer_with_correct_method_is_arithmetic_not_conceptual():
    response = make_response(
        response_id="R-004",
        challenge_id=MEDIUM.challenge_id,
        answer="5",
        reasoning=ARITHMETIC_REASONING,
        learner_confidence=LearnerConfidence.MODERATE,
    )
    evidence = EvidenceAnalyzer().analyze(response, MEDIUM)
    assert evidence.answer_status == AnswerStatus.INCORRECT
    assert evidence.error_type == ErrorPattern.ARITHMETIC
    assert evidence.error_type != ErrorPattern.CONCEPTUAL
    assert evidence.misconception_signal is None


def test_05_ambiguous_response_produces_high_uncertainty():
    response = make_response(
        response_id="R-005",
        challenge_id=MEDIUM.challenge_id,
        answer="Probably B. I'm not sure.",
        reasoning=None,
        learner_confidence=LearnerConfidence.LOW,
    )
    trace = run_one(new_state(), MEDIUM, response)
    assert trace.evidence.answer_status == AnswerStatus.AMBIGUOUS
    assert trace.learner_state_after.uncertainty in {
        Uncertainty.HIGH_UNCERTAINTY,
        Uncertainty.INSUFFICIENT_EVIDENCE,
    }
    assert trace.evidence.diagnostic_confidence in {
        DiagnosticConfidence.LOW,
        DiagnosticConfidence.UNKNOWN,
    }


def test_06_sparse_evidence_is_insufficient_or_weak():
    response = make_response(
        response_id="R-006",
        challenge_id=MEDIUM.challenge_id,
        answer="4",
        reasoning=None,
        learner_confidence=LearnerConfidence.UNKNOWN,
    )
    evidence = EvidenceAnalyzer().analyze(response, MEDIUM)
    assert evidence.answer_status == AnswerStatus.CORRECT
    assert evidence.reasoning_quality == ReasoningQuality.UNKNOWN
    assert evidence.confidence_signal == LearnerConfidence.UNKNOWN
    assert evidence.evidence_strength in {
        EvidenceStrength.INSUFFICIENT,
        EvidenceStrength.WEAK,
    }


def test_07_repeated_misconception_changes_strategy():
    pipeline = AdaptPipeline()
    state = new_state()
    traces = []
    for index in range(3):
        response = make_response(
            response_id=f"R-7{index}",
            challenge_id=DIAGNOSTIC.challenge_id,
            answer="2x+3",
            reasoning=MISCONCEPTION_REASONING,
            learner_confidence=LearnerConfidence.HIGH,
        )
        trace = pipeline.run(
            learner_state=state,
            challenge=DIAGNOSTIC,
            response=response,
        )
        traces.append(trace)
        state = trace.learner_state_after
    decision = traces[-1].adaptation_decision.decision
    assert decision in {
        AdaptationAction.REMEDIATE,
        AdaptationAction.CHANGE_REPRESENTATION,
        AdaptationAction.GATHER_MORE_EVIDENCE,
    }
    assert any(item.misconception_id == DIST_PROP for item in state.repeated_misconceptions)


def test_08_noisy_isolated_error_does_not_cause_extreme_decrease():
    pipeline = AdaptPipeline()
    state = new_state()
    answers = [
        ("4", STRONG_REASONING, LearnerConfidence.HIGH, True),
        ("4", STRONG_REASONING, LearnerConfidence.HIGH, True),
        ("4", STRONG_REASONING, LearnerConfidence.HIGH, True),
        ("5", "I mixed up a sign.", LearnerConfidence.MODERATE, False),
        ("4", STRONG_REASONING, LearnerConfidence.HIGH, True),
        ("4", STRONG_REASONING, LearnerConfidence.HIGH, True),
    ]
    traces = []
    for index, (answer, reasoning, confidence, _ok) in enumerate(answers, start=1):
        response = make_response(
            response_id=f"R-8{index}",
            challenge_id=MEDIUM.challenge_id,
            answer=answer,
            reasoning=reasoning,
            learner_confidence=confidence,
        )
        trace = pipeline.run(learner_state=state, challenge=MEDIUM, response=response)
        traces.append(trace)
        state = trace.learner_state_after
    isolated = traces[3]
    assert isolated.adaptation_decision.decision != AdaptationAction.DECREASE_DIFFICULTY
    assert traces[-1].adaptation_decision.decision != AdaptationAction.DECREASE_DIFFICULTY
    assert traces[-1].next_challenge.difficulty != Difficulty.EASY


def test_09_conflicting_evidence_increases_uncertainty_without_replacing_state():
    pipeline = AdaptPipeline()
    state = new_state()
    for index in range(3):
        response = make_response(
            response_id=f"R-9s{index}",
            challenge_id=MEDIUM.challenge_id,
            answer="4",
            reasoning=STRONG_REASONING,
            learner_confidence=LearnerConfidence.HIGH,
        )
        trace = pipeline.run(learner_state=state, challenge=MEDIUM, response=response)
        state = trace.learner_state_after
    mastery_after_strong = state.mastery_estimate
    uncertainty_after_strong = state.uncertainty
    contradiction = make_response(
        response_id="R-9c",
        challenge_id=MEDIUM.challenge_id,
        answer="0",
        reasoning=GUESS_REASONING,
        learner_confidence=LearnerConfidence.LOW,
    )
    after = pipeline.run(learner_state=state, challenge=MEDIUM, response=contradiction)
    assert after.learner_state_after.uncertainty in {
        Uncertainty.CONTRADICTORY_EVIDENCE,
        Uncertainty.HIGH_UNCERTAINTY,
    }
    assert after.learner_state_after.uncertainty != uncertainty_after_strong or (
        after.learner_state_after.uncertainty == Uncertainty.CONTRADICTORY_EVIDENCE
    )
    drop = mastery_after_strong - after.learner_state_after.mastery_estimate
    assert drop < 0.15
    assert after.learner_state_after.mastery_estimate > 0.45


def test_10_sudden_improvement_sets_improving_trajectory_without_max_difficulty():
    pipeline = AdaptPipeline()
    state = new_state()
    steps = [("0", "I do not know how to isolate x.")] * 3 + [
        ("4", STRONG_REASONING)
    ] * 3
    traces = []
    for index, (answer, reasoning) in enumerate(steps, start=1):
        response = make_response(
            response_id=f"R-10{index}",
            challenge_id=MEDIUM.challenge_id,
            answer=answer,
            reasoning=reasoning,
            learner_confidence=(
                LearnerConfidence.LOW if answer == "0" else LearnerConfidence.HIGH
            ),
        )
        trace = pipeline.run(learner_state=state, challenge=MEDIUM, response=response)
        traces.append(trace)
        state = trace.learner_state_after
    assert state.learning_trajectory == LearningTrajectory.IMPROVING
    assert traces[-1].next_challenge.difficulty != Difficulty.HARD
    assert traces[-1].adaptation_decision.decision != AdaptationAction.INCREASE_DIFFICULTY or (
        traces[-1].next_challenge.difficulty != Difficulty.HARD
    )


def test_11_sudden_regression_sets_regressing_or_uncertainty():
    pipeline = AdaptPipeline()
    state = new_state()
    steps = [("4", STRONG_REASONING, LearnerConfidence.HIGH)] * 3 + [
        ("0", "I subtracted 3 from both sides then got lost.", LearnerConfidence.LOW)
    ] * 2
    traces = []
    for index, (answer, reasoning, confidence) in enumerate(steps, start=1):
        response = make_response(
            response_id=f"R-11{index}",
            challenge_id=MEDIUM.challenge_id,
            answer=answer,
            reasoning=reasoning,
            learner_confidence=confidence,
        )
        trace = pipeline.run(learner_state=state, challenge=MEDIUM, response=response)
        traces.append(trace)
        state = trace.learner_state_after
    assert state.learning_trajectory == LearningTrajectory.REGRESSING or state.uncertainty in {
        Uncertainty.CONTRADICTORY_EVIDENCE,
        Uncertainty.HIGH_UNCERTAINTY,
        Uncertainty.INSUFFICIENT_EVIDENCE,
    }


def test_12_remediate_selects_misconception_targeted_challenge():
    pipeline = AdaptPipeline()
    state = new_state()
    trace = None
    for index in range(3):
        response = make_response(
            response_id=f"R-12{index}",
            challenge_id=DIAGNOSTIC.challenge_id,
            answer="2x+3",
            reasoning=MISCONCEPTION_REASONING,
            learner_confidence=LearnerConfidence.HIGH,
        )
        trace = pipeline.run(learner_state=state, challenge=DIAGNOSTIC, response=response)
        state = trace.learner_state_after
    assert trace is not None
    assert trace.adaptation_decision.decision == AdaptationAction.REMEDIATE
    assert trace.next_challenge.target_misconception == DIST_PROP
    assert "repeated_misconception" in trace.adaptation_decision.reason


def test_determinism_identical_inputs_produce_identical_decisions():
    pipeline = AdaptPipeline()
    response = make_response(
        response_id="R-DET",
        challenge_id=MEDIUM.challenge_id,
        answer="4",
        reasoning=STRONG_REASONING,
        learner_confidence=LearnerConfidence.HIGH,
    )
    first = pipeline.run(learner_state=new_state(), challenge=MEDIUM, response=response)
    second = pipeline.run(learner_state=new_state(), challenge=MEDIUM, response=response)
    assert first.evidence.to_dict() == second.evidence.to_dict()
    assert first.learner_state_after.to_dict() == second.learner_state_after.to_dict()
    assert first.adaptation_decision.to_dict() == second.adaptation_decision.to_dict()
    assert first.next_challenge.challenge_id == second.next_challenge.challenge_id


def test_models_are_serializable_and_round_trip():
    response = make_response(
        response_id="R-SER",
        challenge_id=MEDIUM.challenge_id,
        answer="4",
        reasoning=STRONG_REASONING,
        learner_confidence=LearnerConfidence.HIGH,
    )
    trace = run_one(new_state(), MEDIUM, response)
    payload = json.loads(trace.to_json())
    restored = LearnerState.from_dict(payload["learner_state_after"])
    assert restored.to_dict() == trace.learner_state_after.to_dict()
    Evidence.from_dict(payload["evidence"])


def test_error_handling_rejects_invalid_state_and_missing_challenge():
    with pytest.raises(InvalidLearnerStateError):
        LearnerState.from_dict(
            {
                "learner_id": "L-001",
                "concept_id": "basic_algebra",
                "mastery_estimate": 1.5,
                "confidence": 0.2,
                "reasoning_quality": "UNKNOWN",
                "error_pattern": "NONE",
                "misconceptions": [],
                "recent_performance": {"correct": 0, "incorrect": 0},
                "evidence_strength": "INSUFFICIENT",
                "evidence_reliability": "UNKNOWN",
                "learning_trajectory": "UNKNOWN",
                "uncertainty": "INSUFFICIENT_EVIDENCE",
            }
        )
    with pytest.raises(MissingChallengeError):
        AdaptPipeline().run(
            learner_state=new_state(),
            challenge=None,
            response=make_response(
                response_id="R-ERR",
                challenge_id="ALG-M-001",
                answer="4",
                reasoning=None,
                learner_confidence=LearnerConfidence.UNKNOWN,
            ),
        )
    with pytest.raises(InvalidEvidenceError):
        Evidence.from_dict(
            {
                "response_id": "R-bad",
                "answer_status": "NOT_A_STATUS",
                "reasoning_quality": "STRONG",
                "error_type": "NONE",
                "misconception_signal": None,
                "confidence_signal": "HIGH",
                "evidence_strength": "STRONG",
                "diagnostic_confidence": "HIGH",
            }
        )


def test_weak_evidence_moves_state_less_than_strong_repeated_evidence():
    updater = StateUpdater()
    analyzer = EvidenceAnalyzer()
    weak = analyzer.analyze(
        make_response(
            response_id="R-w",
            challenge_id=MEDIUM.challenge_id,
            answer="4",
            reasoning=GUESS_REASONING,
            learner_confidence=LearnerConfidence.LOW,
        ),
        MEDIUM,
    )
    strong = analyzer.analyze(
        make_response(
            response_id="R-s1",
            challenge_id=MEDIUM.challenge_id,
            answer="4",
            reasoning=STRONG_REASONING,
            learner_confidence=LearnerConfidence.HIGH,
        ),
        MEDIUM,
    )
    start = new_state()
    after_weak = updater.update(start, weak)
    after_one_strong = updater.update(start, strong)
    after_two_strong = updater.update(
        after_one_strong,
        analyzer.analyze(
            make_response(
                response_id="R-s2",
                challenge_id=MEDIUM.challenge_id,
                answer="4",
                reasoning=STRONG_REASONING,
                learner_confidence=LearnerConfidence.HIGH,
            ),
            MEDIUM,
        ),
    )
    weak_move = after_weak.mastery_estimate - start.mastery_estimate
    repeated_move = after_two_strong.mastery_estimate - start.mastery_estimate
    assert weak_move < repeated_move
    assert after_one_strong.mastery_estimate < 0.95


def test_baseline_uses_correctness_only_and_comparison_harness_runs():
    tutor = BaselineTutor()
    lucky = make_response(
        response_id="R-B1",
        challenge_id=MEDIUM.challenge_id,
        answer="4",
        reasoning=GUESS_REASONING,
        learner_confidence=LearnerConfidence.LOW,
    )
    strong = make_response(
        response_id="R-B2",
        challenge_id=MEDIUM.challenge_id,
        answer="4",
        reasoning=STRONG_REASONING,
        learner_confidence=LearnerConfidence.HIGH,
    )
    lucky_result = tutor.respond(MEDIUM, lucky)
    strong_result = tutor.respond(MEDIUM, strong)
    assert lucky_result.answer_status == strong_result.answer_status == AnswerStatus.CORRECT
    assert lucky_result.next_challenge.difficulty == strong_result.next_challenge.difficulty
    adapt_lucky = run_one(new_state("L-base-a"), MEDIUM, lucky)
    adapt_strong = run_one(new_state("L-base-b"), MEDIUM, strong)
    report = compare_sequence(
        [
            adapt_lucky.adaptation_decision.decision.value,
            adapt_strong.adaptation_decision.decision.value,
        ],
        [lucky_result.answer_status.value, strong_result.answer_status.value],
    )
    assert report["baseline_used_correctness_only"] is True
    assert get_challenge("ALG-E-001").difficulty == Difficulty.EASY
