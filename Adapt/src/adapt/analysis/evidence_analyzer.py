"""C-002 (Phase 1C) / C-003 (Phase 1D) Evidence Analyzer.

Deterministic. Missing reasoning or confidence is UNKNOWN, never fabricated.
Correctness is not treated as mastery.
"""

from __future__ import annotations

import re

from adapt.errors import InvalidChallengeError, InvalidLearnerResponseError, MissingChallengeError
from adapt.models.challenge import Challenge
from adapt.models.enums import (
    AnswerStatus,
    DiagnosticConfidence,
    ErrorPattern,
    EvidencePolarity,
    EvidenceReliability,
    EvidenceStrength,
    LearnerConfidence,
    ReasoningQuality,
)
from adapt.models.evidence import Evidence
from adapt.models.learner_response import LearnerResponse

GUESS_RE = re.compile(
    r"\b(i guessed|guessed|just a guess|guessing|i just remembered|"
    r"just remembered|remembered the answer|memorized|random)\b",
    re.IGNORECASE,
)
AMBIGUOUS_RE = re.compile(
    r"\b(probably|i'?m not sure|not sure|maybe|i think|no idea|kind of)\b",
    re.IGNORECASE,
)
ARITHMETIC_RE = re.compile(
    r"\b(arithmetic|calculation (error|mistake)|miscalculat\w*|"
    r"added wrong|multiplied wrong|subtracted wrong|math error|"
    r"comput(ed|ation) (wrong|error)|arithmetic-mistakenly)\b",
    re.IGNORECASE,
)
CARELESS_RE = re.compile(r"\b(typo|slip|careless|misread)\b", re.IGNORECASE)


def _normalize_answer(text: str) -> str:
    cleaned = text.strip().lower()
    cleaned = re.sub(r"^(x\s*=\s*|answer\s*(is|=)\s*)", "", cleaned)
    cleaned = cleaned.replace(" ", "")
    return cleaned


def _contains_cue(text: str, cues: tuple[str, ...]) -> int:
    lowered = text.lower()
    return sum(1 for cue in cues if cue.lower() in lowered)


def _combined_text(response: LearnerResponse) -> str:
    parts = [response.answer or ""]
    if response.reasoning:
        parts.append(response.reasoning)
    return " ".join(parts)


def classify_answer_status(response: LearnerResponse, challenge: Challenge) -> AnswerStatus:
    answer = (response.answer or "").strip()
    if answer == "":
        return AnswerStatus.UNKNOWN

    combined = _combined_text(response)
    expected = challenge.expected_answer
    exact = False
    if expected is not None:
        exact = _normalize_answer(answer) == _normalize_answer(expected) or _normalize_answer(
            expected
        ) in _normalize_answer(answer)

    if AMBIGUOUS_RE.search(combined) and not exact:
        return AnswerStatus.AMBIGUOUS
    if expected is None:
        return AnswerStatus.UNKNOWN
    if exact:
        return AnswerStatus.CORRECT

    expected_norm = _normalize_answer(expected)
    answer_norm = _normalize_answer(answer)
    if expected_norm and expected_norm in answer_norm:
        return AnswerStatus.PARTIAL
    return AnswerStatus.INCORRECT


def classify_reasoning_quality(response: LearnerResponse, challenge: Challenge) -> ReasoningQuality:
    if response.reasoning is None or response.reasoning.strip() == "":
        return ReasoningQuality.UNKNOWN

    text = response.reasoning
    if GUESS_RE.search(text):
        return ReasoningQuality.WEAK

    cue_hits = _contains_cue(text, challenge.expected_reasoning_cues)
    method_hits = _contains_cue(text, challenge.correct_method_cues)
    if cue_hits >= 2 or (cue_hits >= 1 and method_hits >= 1) or method_hits >= 3:
        return ReasoningQuality.STRONG
    if cue_hits >= 1 or method_hits >= 1 or len(text.strip()) > 80:
        return ReasoningQuality.MODERATE
    if len(text.strip()) < 20:
        return ReasoningQuality.WEAK
    return ReasoningQuality.MODERATE


def classify_error_and_misconception(
    response: LearnerResponse,
    challenge: Challenge,
    answer_status: AnswerStatus,
    reasoning_quality: ReasoningQuality,
) -> tuple[ErrorPattern, str | None]:
    if answer_status in {AnswerStatus.CORRECT, AnswerStatus.AMBIGUOUS, AnswerStatus.UNKNOWN}:
        return ErrorPattern.NONE, None

    combined = _combined_text(response)
    for misconception_id, cues in challenge.misconception_cues:
        if _contains_cue(combined, cues) >= 1:
            return ErrorPattern.CONCEPTUAL, misconception_id

    method_hits = _contains_cue(combined, challenge.correct_method_cues)
    if ARITHMETIC_RE.search(combined) or (
        method_hits >= 2 and reasoning_quality in {ReasoningQuality.STRONG, ReasoningQuality.MODERATE}
    ):
        return ErrorPattern.ARITHMETIC, None
    if CARELESS_RE.search(combined):
        return ErrorPattern.CARELESS, None
    if method_hits >= 1:
        return ErrorPattern.PROCEDURAL, None
    if reasoning_quality == ReasoningQuality.UNKNOWN:
        return ErrorPattern.UNKNOWN, None
    return ErrorPattern.CONCEPTUAL, None


def _strength_reliability(
    answer_status: AnswerStatus,
    reasoning_quality: ReasoningQuality,
    confidence_signal: LearnerConfidence,
    error_type: ErrorPattern,
) -> tuple[EvidenceStrength, EvidenceReliability, DiagnosticConfidence, EvidencePolarity]:
    missing_reasoning = reasoning_quality == ReasoningQuality.UNKNOWN
    missing_confidence = confidence_signal == LearnerConfidence.UNKNOWN

    if answer_status == AnswerStatus.UNKNOWN:
        return (
            EvidenceStrength.INSUFFICIENT,
            EvidenceReliability.UNKNOWN,
            DiagnosticConfidence.UNKNOWN,
            EvidencePolarity.NEUTRAL,
        )
    if answer_status == AnswerStatus.AMBIGUOUS:
        return (
            EvidenceStrength.INSUFFICIENT,
            EvidenceReliability.LOW,
            DiagnosticConfidence.LOW,
            EvidencePolarity.NEUTRAL,
        )

    if answer_status == AnswerStatus.CORRECT:
        polarity = EvidencePolarity.POSITIVE
        if missing_reasoning and missing_confidence:
            return (
                EvidenceStrength.INSUFFICIENT,
                EvidenceReliability.LOW,
                DiagnosticConfidence.LOW,
                polarity,
            )
        if reasoning_quality == ReasoningQuality.STRONG and confidence_signal == LearnerConfidence.HIGH:
            return (
                EvidenceStrength.STRONG,
                EvidenceReliability.HIGH,
                DiagnosticConfidence.HIGH,
                polarity,
            )
        if reasoning_quality == ReasoningQuality.STRONG:
            return (
                EvidenceStrength.MODERATE,
                EvidenceReliability.MODERATE,
                DiagnosticConfidence.MODERATE,
                polarity,
            )
        if reasoning_quality == ReasoningQuality.WEAK:
            return (
                EvidenceStrength.WEAK,
                EvidenceReliability.LOW,
                DiagnosticConfidence.LOW,
                polarity,
            )
        if missing_reasoning:
            return (
                EvidenceStrength.WEAK,
                EvidenceReliability.LOW,
                DiagnosticConfidence.LOW,
                polarity,
            )
        return (
            EvidenceStrength.MODERATE,
            EvidenceReliability.MODERATE,
            DiagnosticConfidence.MODERATE,
            polarity,
        )

    polarity = EvidencePolarity.NEGATIVE
    if answer_status == AnswerStatus.PARTIAL:
        polarity = EvidencePolarity.NEUTRAL

    if error_type == ErrorPattern.ARITHMETIC:
        return (
            EvidenceStrength.MODERATE,
            EvidenceReliability.HIGH,
            DiagnosticConfidence.HIGH,
            polarity,
        )
    if error_type == ErrorPattern.CONCEPTUAL and reasoning_quality != ReasoningQuality.UNKNOWN:
        return (
            EvidenceStrength.MODERATE,
            EvidenceReliability.MODERATE,
            DiagnosticConfidence.MODERATE,
            polarity,
        )
    if missing_reasoning and missing_confidence:
        return (
            EvidenceStrength.INSUFFICIENT,
            EvidenceReliability.LOW,
            DiagnosticConfidence.LOW,
            polarity,
        )
    if reasoning_quality == ReasoningQuality.WEAK or missing_reasoning:
        return (
            EvidenceStrength.WEAK,
            EvidenceReliability.LOW,
            DiagnosticConfidence.LOW,
            polarity,
        )
    return (
        EvidenceStrength.MODERATE,
        EvidenceReliability.MODERATE,
        DiagnosticConfidence.MODERATE,
        polarity,
    )


class EvidenceAnalyzer:
    def analyze(
        self,
        response: LearnerResponse,
        challenge: Challenge | None,
        history: list[LearnerResponse] | None = None,
    ) -> Evidence:
        if challenge is None:
            raise MissingChallengeError("Evidence analysis requires a challenge")
        if not isinstance(challenge, Challenge):
            raise InvalidChallengeError("challenge must be a Challenge")
        if not isinstance(response, LearnerResponse):
            raise InvalidLearnerResponseError("response must be a LearnerResponse")
        if response.challenge_id != challenge.challenge_id:
            raise InvalidLearnerResponseError(
                "response.challenge_id does not match challenge.challenge_id"
            )

        answer_status = classify_answer_status(response, challenge)
        reasoning_quality = classify_reasoning_quality(response, challenge)
        confidence_signal = response.learner_confidence
        error_type, misconception_signal = classify_error_and_misconception(
            response, challenge, answer_status, reasoning_quality
        )
        strength, reliability, diagnostic_confidence, polarity = _strength_reliability(
            answer_status, reasoning_quality, confidence_signal, error_type
        )

        # History is available for analysis but must not fabricate missing fields.
        _ = history

        return Evidence(
            response_id=response.response_id,
            answer_status=answer_status,
            reasoning_quality=reasoning_quality,
            error_type=error_type,
            misconception_signal=misconception_signal,
            confidence_signal=confidence_signal,
            evidence_strength=strength,
            diagnostic_confidence=diagnostic_confidence,
            evidence_reliability=reliability,
            polarity=polarity,
        )
