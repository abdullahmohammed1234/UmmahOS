"""Phase 1E fair simple baseline.

Inspects challenge, response, reasoning, confidence, and history.
Does NOT create LearnerState, Evidence, or run StateUpdater / AdaptationEngine.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from adapt.adaptation.challenge_bank import CHALLENGE_BANK
from adapt.analysis.evidence_analyzer import classify_answer_status
from adapt.models.challenge import Challenge
from adapt.models.enums import (
    AnswerStatus,
    ChallengeType,
    Difficulty,
    DIFFICULTY_ORDER,
    LearnerConfidence,
)
from adapt.models.learner_response import LearnerResponse

GUESS_RE = re.compile(
    r"\b(i guessed|guessed|just a guess|guessing|random)\b",
    re.IGNORECASE,
)
AMBIGUOUS_RE = re.compile(
    r"\b(probably|i'?m not sure|not sure|maybe|no idea)\b",
    re.IGNORECASE,
)
ARITHMETIC_RE = re.compile(
    r"\b(arithmetic|calculation (error|mistake)|miscalculat\w*|"
    r"added wrong|math error|arithmetic-mistakenly)\b",
    re.IGNORECASE,
)
WEAK_RE = re.compile(
    r"\b(remembered|memorized|just remembered)\b",
    re.IGNORECASE,
)
MISC_RE = re.compile(
    r"(didn't distribute|did not distribute)",
    re.IGNORECASE,
)
STRONG_HINT_RE = re.compile(
    r"\b(both sides|inverse|isolate|distribute|subtract|divide|sum|difference)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class BaselineDecision:
    decision: str
    diagnosis: str
    reasons: tuple[str, ...]
    next_challenge: Challenge
    answer_status: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "diagnosis": self.diagnosis,
            "reasons": list(self.reasons),
            "next_challenge": self.next_challenge.to_dict(),
            "answer_status": self.answer_status,
        }


def _text(response: LearnerResponse) -> str:
    return f"{response.answer or ''} {response.reasoning or ''}"


def _shift(current: Difficulty, delta: int) -> Difficulty:
    index = DIFFICULTY_ORDER.index(current)
    return DIFFICULTY_ORDER[min(len(DIFFICULTY_ORDER) - 1, max(0, index + delta))]


def _pick(
    bank: tuple[Challenge, ...],
    *,
    difficulty: Difficulty | None,
    challenge_type: ChallengeType | None,
    current_id: str,
    target_misconception: str | None = None,
) -> Challenge:
    candidates = [
        item
        for item in bank
        if item.challenge_id != current_id
        and (difficulty is None or item.difficulty == difficulty)
        and (challenge_type is None or item.challenge_type == challenge_type)
        and (target_misconception is None or item.target_misconception == target_misconception)
    ]
    if candidates:
        return candidates[0]
    fallback = [item for item in bank if item.challenge_id != current_id]
    return fallback[0] if fallback else bank[0]


class BenchmarkBaseline:
    """Simple direct if-then tutor. Documented heuristics, no learner-state pipeline."""

    def __init__(self, bank: tuple[Challenge, ...] | None = None) -> None:
        self.bank = bank or CHALLENGE_BANK

    def respond(
        self,
        challenge: Challenge,
        response: LearnerResponse,
        history: list[tuple[Challenge, LearnerResponse]],
    ) -> BaselineDecision:
        status = classify_answer_status(response, challenge)
        text = _text(response)
        hist_status = [classify_answer_status(item[1], item[0]) for item in history]
        misc_count = sum(
            1
            for ch, resp in list(history) + [(challenge, response)]
            if MISC_RE.search(_text(resp))
        )
        reasons: list[str] = []

        if AMBIGUOUS_RE.search(text) and status != AnswerStatus.CORRECT:
            reasons.append("ambiguous_language")
            decision = "PROBE_UNCERTAINTY"
        elif GUESS_RE.search(text):
            reasons.append("guess_language")
            decision = "GATHER_MORE_EVIDENCE"
        elif (response.reasoning is None or response.reasoning.strip() == "") and (
            response.learner_confidence == LearnerConfidence.UNKNOWN
        ):
            reasons.append("missing_reasoning_and_confidence")
            decision = "GATHER_MORE_EVIDENCE"
        elif misc_count >= 3:
            reasons.append("repeated_misconception_keywords")
            decision = "REMEDIATE"
        elif status == AnswerStatus.INCORRECT and ARITHMETIC_RE.search(text):
            reasons.append("arithmetic_language")
            decision = "MAINTAIN_DIFFICULTY"
        elif (
            status == AnswerStatus.INCORRECT
            and len(hist_status) >= 3
            and hist_status[-3:].count(AnswerStatus.CORRECT) == 3
        ):
            reasons.append("isolated_error_after_success")
            decision = "MAINTAIN_DIFFICULTY"
        elif len(hist_status) + 1 >= 6:
            seq = hist_status + [status]
            early = seq[-6:-3]
            late = seq[-3:]
            incorrectish = {AnswerStatus.INCORRECT, AnswerStatus.AMBIGUOUS, AnswerStatus.UNKNOWN}
            if all(item in incorrectish for item in early) and all(
                item == AnswerStatus.CORRECT for item in late
            ):
                reasons.append("sudden_improvement")
                decision = "MAINTAIN_DIFFICULTY"
            else:
                decision = None  # type: ignore[assignment]
        else:
            decision = None  # type: ignore[assignment]

        if decision is None:
            if (
                status == AnswerStatus.INCORRECT
                and len(hist_status) >= 4
                and hist_status[-1] == AnswerStatus.INCORRECT
                and hist_status[:-1].count(AnswerStatus.CORRECT) >= 3
            ):
                reasons.append("recent_regression")
                decision = "DECREASE_DIFFICULTY"
            elif (
                status == AnswerStatus.INCORRECT
                and hist_status
                and hist_status.count(AnswerStatus.CORRECT) / len(hist_status) >= 0.7
            ):
                reasons.append("contradicts_successful_history")
                decision = "GATHER_MORE_EVIDENCE"
            elif status == AnswerStatus.CORRECT and WEAK_RE.search(text):
                reasons.append("weak_reasoning")
                decision = "MAINTAIN_DIFFICULTY"
            elif (
                status == AnswerStatus.CORRECT
                and STRONG_HINT_RE.search(text)
                and response.learner_confidence == LearnerConfidence.HIGH
                and hist_status.count(AnswerStatus.CORRECT) >= 2
            ):
                reasons.append("correct_strong_reasoning_repeated_success")
                decision = "INCREASE_DIFFICULTY"
            elif status == AnswerStatus.CORRECT:
                reasons.append("correct_answer")
                decision = "INCREASE_DIFFICULTY"
            elif status == AnswerStatus.AMBIGUOUS:
                reasons.append("ambiguous_answer_status")
                decision = "PROBE_UNCERTAINTY"
            else:
                reasons.append("incorrect_answer")
                decision = "DECREASE_DIFFICULTY"

        next_challenge = self._next_challenge(decision, challenge)
        diagnosis = (
            f"Baseline used correctness={status.value} with heuristic reasons: "
            + ", ".join(reasons)
        )
        return BaselineDecision(
            decision=decision,
            diagnosis=diagnosis,
            reasons=tuple(reasons),
            next_challenge=next_challenge,
            answer_status=status.value,
        )

    def _next_challenge(self, decision: str, challenge: Challenge) -> Challenge:
        if decision == "INCREASE_DIFFICULTY":
            return _pick(
                self.bank,
                difficulty=_shift(challenge.difficulty, 1),
                challenge_type=ChallengeType.PRACTICE,
                current_id=challenge.challenge_id,
            )
        if decision == "DECREASE_DIFFICULTY":
            return _pick(
                self.bank,
                difficulty=_shift(challenge.difficulty, -1),
                challenge_type=ChallengeType.PRACTICE,
                current_id=challenge.challenge_id,
            )
        if decision == "REMEDIATE":
            return _pick(
                self.bank,
                difficulty=None,
                challenge_type=ChallengeType.REMEDIATION,
                current_id=challenge.challenge_id,
                target_misconception="DIST_PROP",
            )
        if decision in {"PROBE_UNCERTAINTY", "GATHER_MORE_EVIDENCE"}:
            return _pick(
                self.bank,
                difficulty=None,
                challenge_type=ChallengeType.DIAGNOSTIC,
                current_id=challenge.challenge_id,
            )
        if decision == "CHANGE_REPRESENTATION":
            return _pick(
                self.bank,
                difficulty=None,
                challenge_type=ChallengeType.DIAGNOSTIC,
                current_id=challenge.challenge_id,
            )
        return _pick(
            self.bank,
            difficulty=challenge.difficulty,
            challenge_type=ChallengeType.PRACTICE,
            current_id=challenge.challenge_id,
        )
