"""Learner- and research-facing presentation of engine traces.

Templates are keyed off actual evidence, strategy, and reason codes.
This module does not decide the next challenge or strategy.
"""

from __future__ import annotations

from typing import Any

from adapt.models.enums import AnswerStatus, Difficulty, ReasoningQuality, StrategyName
from adapt.models.evidence import Evidence
from adapt.models.learner_state import LearnerState
from adapt.product.labels import strategy_label
from adapt.product.topics import CONCEPT_LABELS, topic_for_concept
from adapt.product.trace_explain import human_trace_explanation
from adapt.tutor.session import StepTrace, TutorSession

LEARNER_STRATEGY_MESSAGES = {
    StrategyName.INCREASE: (
        "You're showing strong understanding. Let's raise the challenge."
    ),
    StrategyName.MAINTAIN: (
        "You're progressing well. Let's reinforce this level with another variation."
    ),
    StrategyName.PROBE: (
        "Let's try a quick check to understand this concept more clearly."
    ),
    StrategyName.REMEDIATE: (
        "Let's approach this concept from another angle."
    ),
    StrategyName.GATHER_EVIDENCE: (
        "Let's try one more challenge before deciding what comes next."
    ),
    StrategyName.DECREASE: (
        "Let's step back and build this up from a simpler version."
    ),
    StrategyName.ASSESS: (
        "Let's start by seeing how you approach this concept."
    ),
    StrategyName.RECOVER: (
        "Your responses improved. Let's move forward from here."
    ),
}

CODE_SUPPORTING = (
    (
        "strong_reasoning",
        "Your reasoning shows a strong understanding of the concept.",
    ),
    (
        "weak_reasoning",
        "Your answer was correct, but your reasoning suggests we should check this concept a little more.",
    ),
    (
        "delayed_or_isolated_misconception",
        "You showed a specific mix-up after strong work, so we're checking this concept one more way.",
    ),
    (
        "persistent_misconception_evidence",
        "The same mix-up appeared again, so we'll rebuild this idea from another angle.",
    ),
    (
        "repeated_misconception",
        "The same mix-up appeared again, so we'll rebuild this idea from another angle.",
    ),
    (
        "strategy_recovery",
        "Your recent responses improved, so ADAPT is leaving the extra support path.",
    ),
    (
        "successful_remediation",
        "Your recent responses improved, so ADAPT is leaving the extra support path.",
    ),
    (
        "sparse_evidence",
        "ADAPT is still learning how you think about this concept.",
    ),
    (
        "gather_before_commit",
        "ADAPT is still learning how you think about this concept.",
    ),
    (
        "insufficient_evidence",
        "There isn't enough yet to change course, so we'll gather a bit more evidence.",
    ),
    (
        "confidence_mastery_conflict",
        "The answer was right, but the reasoning and confidence don't fully line up yet.",
    ),
    (
        "high_uncertainty",
        "You showed some uncertainty, so we're giving you a quick check before moving ahead.",
    ),
    (
        "localized_error",
        "This looks like a local mix-up, not a reason to start over.",
    ),
    (
        "global_regression",
        "Recent work suggests this is harder than it looked, so we'll simplify.",
    ),
    (
        "strong_recent_evidence",
        "The evidence of understanding is strong enough to raise the challenge.",
    ),
    (
        "maintain_until_stronger_signal",
        "You're progressing well. Let's stay at this level with another variation.",
    ),
)

ARROW = {"up": "↑", "down": "↓", "same": "→"}


def learner_strategy_message(strategy: StrategyName) -> str:
    return LEARNER_STRATEGY_MESSAGES[strategy]


def challenge_view(challenge, *, include_answer: bool = False) -> dict[str, Any]:
    payload = {
        "challenge_id": challenge.challenge_id,
        "prompt": challenge.question,
        "concept_id": challenge.concept_id,
        "difficulty": challenge.difficulty.value,
        "challenge_type": challenge.challenge_type.value,
        "unavailable": challenge.challenge_id == "UNAVAILABLE",
    }
    if include_answer:
        payload["expected_answer"] = challenge.expected_answer
    return payload


def feedback_from_evidence(evidence: Evidence) -> dict[str, Any]:
    if evidence.answer_status == AnswerStatus.CORRECT:
        headline = "Correct"
        tone = "success"
        if evidence.reasoning_quality == ReasoningQuality.STRONG:
            detail = "Your reasoning shows a strong understanding of the concept."
        elif evidence.reasoning_quality == ReasoningQuality.WEAK:
            detail = (
                "Your answer was correct, but your reasoning suggests "
                "we should check this concept a little more."
            )
        elif evidence.reasoning_quality == ReasoningQuality.UNKNOWN:
            detail = (
                "You got the answer. Sharing your reasoning next time helps ADAPT "
                "understand how you thought about it."
            )
        else:
            detail = (
                "You're on the right track. A bit more explanation will help ADAPT "
                "understand your thinking."
            )
    else:
        headline = "Needs another look"
        tone = "retry"
        if evidence.misconception_signal:
            detail = (
                "Your reasoning points to a specific mix-up. "
                "We'll approach this concept from another angle."
            )
        elif evidence.reasoning_quality == ReasoningQuality.STRONG:
            detail = (
                "Your method is thoughtful, but the result didn't match. "
                "Let's check this another way."
            )
        else:
            detail = "This one didn't land. We'll try a different path so the idea can click."
    return {
        "headline": headline,
        "tone": tone,
        "detail": detail,
        "answer_status": evidence.answer_status.value,
        "reasoning_quality": evidence.reasoning_quality.value,
        "misconception_signal": evidence.misconception_signal,
    }


def supporting_from_codes(reason_codes: tuple[str, ...], fallback: str) -> str:
    code_set = set(reason_codes)
    for code, sentence in CODE_SUPPORTING:
        if code in code_set:
            return sentence
    return fallback


def adaptation_from_step(step: StepTrace) -> dict[str, Any]:
    changed = step.strategy_before.current_strategy != step.strategy_after.current_strategy
    message = learner_strategy_message(step.decision)
    supporting = supporting_from_codes(step.reason_codes, message)
    explanation = human_trace_explanation(step)
    mastery_arrow = ARROW[delta_arrow(step.state_before.mastery_estimate, step.state_after.mastery_estimate)]
    if changed or step.decision in {
        StrategyName.INCREASE,
        StrategyName.PROBE,
        StrategyName.REMEDIATE,
        StrategyName.DECREASE,
        StrategyName.RECOVER,
    }:
        headline = "ADAPTATION DETECTED"
    else:
        headline = "ADAPT is staying with this approach"
    next_difficulty = step.next_challenge.difficulty
    current_difficulty = step.challenge.difficulty
    if next_difficulty == Difficulty.HARD and current_difficulty != Difficulty.HARD:
        next_line = f"Harder {concept_label(step.next_challenge.concept_id).lower()} challenge"
    elif next_difficulty == Difficulty.EASY and current_difficulty != Difficulty.EASY:
        next_line = f"Simpler {concept_label(step.next_challenge.concept_id).lower()} challenge"
    else:
        next_line = f"Next {concept_label(step.next_challenge.concept_id).lower()} challenge"
    return {
        "visible": True,
        "strategy_changed": changed,
        "headline": headline,
        "message": message,
        "supporting": supporting,
        "decision": step.decision.value,
        "decision_label": strategy_label(step.decision),
        "reason": step.reason,
        "reason_codes": list(step.reason_codes),
        "mastery_arrow": mastery_arrow,
        "state_line": f"Mastery {mastery_arrow}",
        "next_line": next_line,
        "evidence_line": explanation["evidence"],
        "explanation": explanation,
    }


def delta_arrow(before: float, after: float, *, epsilon: float = 0.005) -> str:
    if after - before > epsilon:
        return "up"
    if before - after > epsilon:
        return "down"
    return "same"


def understanding_view(state: LearnerState) -> dict[str, Any]:
    level = max(0.0, min(1.0, float(state.mastery_estimate)))
    filled = max(0, min(10, round(level * 10)))
    if level >= 0.8:
        label = "Strong"
    elif level >= 0.6:
        label = "Growing"
    elif level >= 0.4:
        label = "Developing"
    else:
        label = "Building"
    return {
        "level": round(level, 4),
        "filled": filled,
        "bar": ("█" * filled) + ("░" * (10 - filled)),
        "label": label,
    }


def research_state_view(before: LearnerState, after: LearnerState) -> dict[str, Any]:
    return {
        "mastery": round(after.mastery_estimate, 4),
        "mastery_before": round(before.mastery_estimate, 4),
        "mastery_arrow": ARROW[delta_arrow(before.mastery_estimate, after.mastery_estimate)],
        "confidence": round(after.confidence, 4),
        "confidence_before": round(before.confidence, 4),
        "confidence_arrow": ARROW[delta_arrow(before.confidence, after.confidence)],
        "evidence_strength": after.evidence_strength.value,
        "uncertainty": after.uncertainty.value,
        "trajectory": after.learning_trajectory.value,
        "reasoning_quality": after.reasoning_quality.value,
    }


def evidence_view(evidence: Evidence) -> dict[str, Any]:
    return {
        "answer_status": evidence.answer_status.value,
        "reasoning_quality": evidence.reasoning_quality.value,
        "confidence_signal": evidence.confidence_signal.value,
        "evidence_strength": evidence.evidence_strength.value,
        "misconception_signal": evidence.misconception_signal,
        "error_type": evidence.error_type.value,
        "polarity": evidence.polarity.value,
        "diagnostic_confidence": evidence.diagnostic_confidence.value,
    }


def chain_link(step: StepTrace, *, include_answers: bool = True) -> dict[str, Any]:
    """One evidence → state → strategy → challenge link from an actual trace."""
    return {
        "step_number": step.step_number,
        "complete": step.is_complete(),
        "response": {
            "answer": step.response.answer,
            "reasoning": step.response.reasoning,
            "learner_confidence": step.response.learner_confidence.value,
            "correct": step.evidence.answer_status == AnswerStatus.CORRECT,
        },
        "evidence": evidence_view(step.evidence),
        "state": research_state_view(step.state_before, step.state_after),
        "strategy": {
            "before": step.strategy_before.current_strategy.value,
            "after": step.strategy_after.current_strategy.value,
            "decision": step.decision.value,
            "reason": step.reason,
            "reason_codes": list(step.reason_codes),
            "adaptation_action": step.adaptation_action.value,
        },
        "challenge": challenge_view(step.challenge, include_answer=include_answers),
        "next_challenge": challenge_view(step.next_challenge, include_answer=include_answers),
        "explanation": step.explanation,
        "human_explanation": human_trace_explanation(step),
        "feedback": feedback_from_evidence(step.evidence),
        "adaptation": adaptation_from_step(step),
    }


def timeline_from_session(session: TutorSession) -> list[dict[str, Any]]:
    items = []
    items.append(
        {
            "step": 0,
            "strategy": session.traces[0].strategy_before.current_strategy.value
            if session.traces
            else session.strategy_state.current_strategy.value,
            "label": "start",
        }
    )
    for step in session.traces:
        items.append(
            {
                "step": step.step_number,
                "strategy": step.decision.value,
                "label": step.decision.value,
                "changed": step.strategy_before.current_strategy != step.strategy_after.current_strategy,
            }
        )
    return items


def concept_label(concept_id: str) -> str:
    topic = topic_for_concept(concept_id)
    if topic is not None:
        return topic.name
    try:
        from adapt.content.catalog import CATALOG

        label = CATALOG.concept_label(concept_id)
        if label != concept_id:
            return label
    except Exception:
        pass
    return CONCEPT_LABELS.get(concept_id, concept_id)
