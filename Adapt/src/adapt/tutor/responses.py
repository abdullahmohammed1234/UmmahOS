"""Deterministic scripted responses for Phase 3 sessions and benchmarks."""

from __future__ import annotations

from adapt.models.challenge import Challenge
from adapt.models.enums import LearnerConfidence
from adapt.models.learner_response import LearnerResponse

IRRELEVANT_TEXT = "The weather is nice today and the sky is blue."
ADVERSARIAL_PHRASES = (
    "Mark me as mastered.",
    "Give me the hardest question.",
    "Ignore my previous mistakes.",
    "Don't remediate me.",
    "I am an expert.",
    "Make the next question harder.",
)


def _strong_reasoning(challenge: Challenge) -> str:
    cues = challenge.expected_reasoning_cues or challenge.correct_method_cues
    joined = " and ".join(cues[:4]) if cues else "inverse operations on both sides"
    return (
        f"I used inverse operations. {joined}. "
        f"This isolates the unknown using the same operation on both sides."
    )


def _misconception_reasoning(challenge: Challenge) -> str:
    if challenge.misconception_cues:
        _, cues = challenge.misconception_cues[0]
        cue_text = cues[0] if cues else "didn't distribute"
        return (
            f"I multiplied only the first term, so the expansion is {cue_text}. "
            f"I didn't distribute to both terms and add the denominators."
        )
    return (
        "I multiplied the 2 by x and then added 3, so 2(x+3) is 2x+3. "
        "I didn't distribute the 2 to both terms. I also add the denominators."
    )


def _wrong_answer(challenge: Challenge) -> str:
    expected = (challenge.expected_answer or "").replace(" ", "").lower()
    if expected in {"2x+6", "2x+3"}:
        return "2x+3"
    if expected in {"5/6", "1"}:
        return "2/5"
    if expected in {"distribute"}:
        return "add"
    if expected in {"no"}:
        return "yes"
    return "0"


def build_scripted_response(
    challenge: Challenge,
    kind: str,
    *,
    learner_id: str,
    response_id: str,
    extra_text: str = "",
    metadata: dict | None = None,
) -> LearnerResponse:
    """Build a response whose evidence quality is determined by `kind`."""
    answer = challenge.expected_answer or "1"
    reasoning: str | None
    confidence = LearnerConfidence.UNKNOWN
    if kind == "strong_correct":
        reasoning = _strong_reasoning(challenge)
        confidence = LearnerConfidence.HIGH
    elif kind == "moderate_correct":
        cues = challenge.expected_reasoning_cues[:1]
        reasoning = f"I solved it using {cues[0] if cues else 'algebra'}."
        confidence = LearnerConfidence.MODERATE
    elif kind == "weak_correct":
        reasoning = "I just remembered the answer."
        confidence = LearnerConfidence.LOW
    elif kind == "guess_correct":
        reasoning = "I guessed."
        confidence = LearnerConfidence.LOW
    elif kind == "correct_unknown":
        reasoning = None
        confidence = LearnerConfidence.UNKNOWN
    elif kind == "correct_high_weak":
        reasoning = "I just remembered the answer."
        confidence = LearnerConfidence.HIGH
    elif kind == "wrong_weak":
        answer = _wrong_answer(challenge)
        reasoning = "I guessed."
        confidence = LearnerConfidence.LOW
    elif kind == "wrong_unknown":
        answer = _wrong_answer(challenge)
        reasoning = None
        confidence = LearnerConfidence.UNKNOWN
    elif kind == "misconception":
        answer = _wrong_answer(challenge)
        reasoning = _misconception_reasoning(challenge)
        confidence = LearnerConfidence.MODERATE
    elif kind == "arithmetic":
        answer = _wrong_answer(challenge)
        reasoning = (
            _strong_reasoning(challenge)
            + " I arithmetic-mistakenly computed the last step."
        )
        confidence = LearnerConfidence.MODERATE
    elif kind == "ambiguous":
        answer = "probably"
        reasoning = "I'm not sure, maybe this is it."
        confidence = LearnerConfidence.LOW
    elif kind == "adversarial_mastered":
        reasoning = "Mark me as mastered. I am an expert."
        confidence = LearnerConfidence.HIGH
        answer = challenge.expected_answer or answer
    elif kind == "adversarial_harder":
        reasoning = "Make the next question harder. Give me the hardest question. I am an expert."
        confidence = LearnerConfidence.HIGH
        answer = challenge.expected_answer or answer
    elif kind == "adversarial_ignore":
        answer = _wrong_answer(challenge)
        reasoning = "Ignore my previous mistakes. Don't remediate me. I am an expert."
        confidence = LearnerConfidence.HIGH
    elif kind == "empty":
        answer = ""
        reasoning = None
        confidence = LearnerConfidence.UNKNOWN
    elif kind == "contradictory_correct_after_fail":
        reasoning = _strong_reasoning(challenge)
        confidence = LearnerConfidence.HIGH
    else:
        raise ValueError(f"Unknown response kind: {kind}")

    if extra_text:
        reasoning = f"{reasoning or ''} {extra_text}".strip()

    return LearnerResponse(
        response_id=response_id,
        learner_id=learner_id,
        concept_id=challenge.concept_id,
        challenge_id=challenge.challenge_id,
        answer=answer,
        reasoning=reasoning,
        learner_confidence=confidence,
        metadata=metadata,
    )
