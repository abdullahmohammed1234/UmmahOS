"""BASELINE-001: a deterministic tutor without the ADAPT state/evidence pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from adapt.adaptation.challenge_bank import CHALLENGE_BANK
from adapt.analysis.evidence_analyzer import classify_answer_status
from adapt.errors import MissingChallengeError
from adapt.models.challenge import Challenge
from adapt.models.enums import AnswerStatus, ChallengeType, Difficulty, DIFFICULTY_ORDER
from adapt.models.learner_response import LearnerResponse


@dataclass(frozen=True)
class BaselineResult:
    diagnosis: str
    next_challenge: Challenge
    answer_status: AnswerStatus

    def to_dict(self) -> dict[str, Any]:
        return {
            "diagnosis": self.diagnosis,
            "next_challenge": self.next_challenge.to_dict(),
            "answer_status": self.answer_status.value,
        }


def _shift(current: Difficulty, delta: int) -> Difficulty:
    index = DIFFICULTY_ORDER.index(current)
    return DIFFICULTY_ORDER[min(len(DIFFICULTY_ORDER) - 1, max(0, index + delta))]


class BaselineTutor:
    """Correctness-only next-challenge policy. No learner state is maintained."""

    def __init__(self, bank: tuple[Challenge, ...] | None = None) -> None:
        self.bank = bank or CHALLENGE_BANK

    def respond(
        self,
        challenge: Challenge | None,
        response: LearnerResponse,
        history: list[LearnerResponse] | None = None,
    ) -> BaselineResult:
        if challenge is None:
            raise MissingChallengeError("baseline tutor requires a challenge")
        _ = history
        status = classify_answer_status(response, challenge)
        if status == AnswerStatus.CORRECT:
            target = _shift(challenge.difficulty, 1)
            diagnosis = "Answer marked correct. Increasing difficulty."
        else:
            target = _shift(challenge.difficulty, -1)
            diagnosis = "Answer marked incorrect. Decreasing difficulty."

        candidates = [
            item
            for item in self.bank
            if item.difficulty == target
            and item.challenge_type == ChallengeType.PRACTICE
            and item.challenge_id != challenge.challenge_id
        ]
        if not candidates:
            candidates = [
                item for item in self.bank if item.challenge_id != challenge.challenge_id
            ]
        next_challenge = candidates[0] if candidates else challenge
        return BaselineResult(
            diagnosis=diagnosis,
            next_challenge=next_challenge,
            answer_status=status,
        )


def compare_sequence(
    adapt_decisions: list[str],
    baseline_statuses: list[str],
) -> dict[str, Any]:
    """Minimal comparison harness for the same response sequence."""
    return {
        "adapt_decisions": list(adapt_decisions),
        "baseline_used_correctness_only": True,
        "baseline_answer_statuses": list(baseline_statuses),
        "adapt_unique_decisions": sorted(set(adapt_decisions)),
        "decision_count": len(adapt_decisions),
    }
