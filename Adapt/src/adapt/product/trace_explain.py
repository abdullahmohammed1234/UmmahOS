"""Human-readable explanations generated from actual engine traces.

Never claims evidence that was not present on the step.
Does not choose strategy or the next challenge.
"""

from __future__ import annotations

from typing import Any

from adapt.models.enums import AnswerStatus, Difficulty, ReasoningQuality, StrategyName
from adapt.models.evidence import Evidence
from adapt.models.learner_state import LearnerState
from adapt.product.labels import strategy_label
from adapt.product.topics import CONCEPT_LABELS, topic_for_concept
from adapt.tutor.session import StepTrace

_DIFFICULTY_RANK = {
    Difficulty.EASY: 0,
    Difficulty.MEDIUM: 1,
    Difficulty.HARD: 2,
}


def _concept_label(concept_id: str) -> str:
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


def _delta_arrow(before: float, after: float, *, epsilon: float = 0.005) -> str:
    if after - before > epsilon:
        return "up"
    if before - after > epsilon:
        return "down"
    return "same"


def _answer_phrase(evidence: Evidence) -> str | None:
    if evidence.answer_status == AnswerStatus.CORRECT:
        return "Correct answer"
    if evidence.answer_status == AnswerStatus.INCORRECT:
        return "Incorrect answer"
    if evidence.answer_status == AnswerStatus.PARTIAL:
        return "Partial answer"
    if evidence.answer_status == AnswerStatus.AMBIGUOUS:
        return "Ambiguous answer"
    return None


def _reasoning_phrase(evidence: Evidence) -> str | None:
    if evidence.reasoning_quality == ReasoningQuality.STRONG:
        return "strong reasoning"
    if evidence.reasoning_quality == ReasoningQuality.MODERATE:
        return "moderate reasoning"
    if evidence.reasoning_quality == ReasoningQuality.WEAK:
        return "weak reasoning"
    return None


def _confidence_phrase(evidence: Evidence) -> str | None:
    value = evidence.confidence_signal.value
    if value == "HIGH":
        return "high confidence"
    if value == "MODERATE":
        return "moderate confidence"
    if value == "LOW":
        return "low confidence"
    return None


def evidence_summary(evidence: Evidence) -> str:
    parts: list[str] = []
    answer = _answer_phrase(evidence)
    reasoning = _reasoning_phrase(evidence)
    confidence = _confidence_phrase(evidence)
    if answer:
        parts.append(answer)
    if reasoning:
        parts.append(reasoning)
    if confidence:
        parts.append(confidence)
    if evidence.misconception_signal:
        parts.append("misconception signal")
    if not parts:
        return "Limited evidence was available from this response."
    return " + ".join(parts)


def evidence_question(evidence: Evidence) -> str:
    if evidence.misconception_signal:
        return "The response suggested a specific mix-up, not only a right or wrong answer."
    if (
        evidence.answer_status == AnswerStatus.CORRECT
        and evidence.reasoning_quality == ReasoningQuality.STRONG
    ):
        return "The response showed conceptual understanding, not only a correct result."
    if (
        evidence.answer_status == AnswerStatus.CORRECT
        and evidence.reasoning_quality == ReasoningQuality.WEAK
    ):
        return "The answer was correct, but the reasoning did not show how the learner got there."
    if evidence.answer_status == AnswerStatus.CORRECT and evidence.reasoning_quality == ReasoningQuality.UNKNOWN:
        return "The answer was correct, but there was little reasoning to interpret."
    if evidence.answer_status == AnswerStatus.INCORRECT and evidence.reasoning_quality == ReasoningQuality.STRONG:
        return "The method looked thoughtful, but the result did not match."
    if evidence.answer_status in {AnswerStatus.INCORRECT, AnswerStatus.PARTIAL}:
        return "The response showed that this idea has not landed yet."
    return "The response gave ADAPT another observation about how this learner is thinking."


def _mastery_reason(evidence: Evidence, arrow: str) -> str:
    if arrow == "up":
        if (
            evidence.answer_status == AnswerStatus.CORRECT
            and evidence.reasoning_quality == ReasoningQuality.STRONG
        ):
            return (
                "Mastery increased because multiple evidence signals "
                "supported conceptual understanding."
            )
        if evidence.answer_status == AnswerStatus.CORRECT:
            return "Mastery increased because the answer was correct."
        return "Mastery increased based on the evidence from this response."
    if arrow == "down":
        if evidence.misconception_signal:
            return "Mastery decreased because a misconception signal was present."
        if evidence.answer_status == AnswerStatus.INCORRECT:
            return "Mastery decreased because the answer was not correct."
        return "Mastery decreased based on the evidence from this response."
    return "Mastery stayed about the same after this response."


def state_explanation(before: LearnerState, after: LearnerState, evidence: Evidence) -> str:
    arrow = _delta_arrow(before.mastery_estimate, after.mastery_estimate)
    return _mastery_reason(evidence, arrow)


def strategy_explanation(step: StepTrace) -> str:
    decision = step.decision
    evidence = step.evidence
    if decision == StrategyName.INCREASE:
        return "Increase difficulty because the learner appears ready for a more challenging task."
    if decision == StrategyName.PROBE:
        return "Probe the concept because the evidence is still uncertain or incomplete."
    if decision == StrategyName.REMEDIATE:
        if evidence.misconception_signal:
            return "Remediate because a misconception signal was present."
        return "Remediate because the evidence shows this idea needs another approach."
    if decision == StrategyName.DECREASE:
        return "Decrease difficulty because the evidence indicates this level is too hard right now."
    if decision == StrategyName.GATHER_EVIDENCE:
        return "Gather more evidence before committing to a larger instructional change."
    if decision == StrategyName.ASSESS:
        return "Assess understanding because there is not yet enough evidence to assume mastery."
    if decision == StrategyName.RECOVER:
        return "Recover because recent responses improved after extra support."
    if decision == StrategyName.MAINTAIN:
        return "Stay at this level with another variation while evidence accumulates."
    return step.reason


def next_challenge_explanation(step: StepTrace) -> str:
    current = step.challenge
    nxt = step.next_challenge
    concept = _concept_label(nxt.concept_id)
    if nxt.challenge_id == "UNAVAILABLE":
        return "No further challenge was available in the current bank."
    current_rank = _DIFFICULTY_RANK.get(current.difficulty, 1)
    next_rank = _DIFFICULTY_RANK.get(nxt.difficulty, 1)
    if step.decision == StrategyName.PROBE:
        return f"A check was selected to clarify {concept.lower()} understanding."
    if step.decision == StrategyName.REMEDIATE:
        return f"A remediation challenge was selected for {concept.lower()}."
    if step.decision == StrategyName.GATHER_EVIDENCE:
        return f"Another {concept.lower()} challenge was selected to gather more evidence."
    if step.decision == StrategyName.INCREASE or next_rank > current_rank:
        return f"A harder {concept.lower()} challenge was selected."
    if step.decision == StrategyName.DECREASE or next_rank < current_rank:
        return f"A simpler {concept.lower()} challenge was selected."
    return f"The next {concept.lower()} challenge was selected from the engine's challenge bank."


def human_trace_explanation(step: StepTrace) -> dict[str, Any]:
    evidence = step.evidence
    return {
        "evidence": evidence_summary(evidence),
        "evidence_detail": evidence_question(evidence),
        "state": state_explanation(step.state_before, step.state_after, evidence),
        "strategy": strategy_explanation(step),
        "strategy_label": strategy_label(step.decision),
        "next_challenge": next_challenge_explanation(step),
        "decision": step.decision.value,
        "reason": step.reason,
        "reason_codes": list(step.reason_codes),
        "misconception_signal": evidence.misconception_signal,
        "answer_status": evidence.answer_status.value,
        "reasoning_quality": evidence.reasoning_quality.value,
        "confidence_signal": evidence.confidence_signal.value,
    }
