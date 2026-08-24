"""Phase 5 fair non-adaptive tutoring baseline.

A linear practice tutor: same topics, comparable difficulty mix, feedback after
each item, fixed sequence. Next challenge is position in a frozen list.

This module must not import AdaptiveTutor, ProductService, strategy, or state.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from adapt.analysis.evidence_analyzer import classify_answer_status
from adapt.eval.constants import BASELINE_SEQUENCE, RANDOM_SEED
from adapt.models.challenge import Challenge
from adapt.models.enums import AnswerStatus, LearnerConfidence
from adapt.models.learner_response import LearnerResponse
from adapt.tutor.challenge_bank import PHASE3_BY_ID


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _feedback(status: AnswerStatus, challenge: Challenge) -> dict[str, str]:
    method = " ".join(challenge.correct_method_cues[:3]).strip()
    if status == AnswerStatus.CORRECT:
        detail = "You got this one."
        if method:
            detail += f" The useful idea here is: {method}."
        return {"headline": "Correct", "tone": "success", "detail": detail}
    detail = "This one didn't match the expected result."
    if method:
        detail += f" A standard approach uses: {method}."
    return {"headline": "Needs another look", "tone": "retry", "detail": detail}


@dataclass(frozen=True)
class BaselineStep:
    step_number: int
    challenge_id: str
    answer: str
    confidence: str
    reasoning: str | None
    answer_status: str
    feedback: dict[str, str]
    next_challenge_id: str | None
    timestamp: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_number": self.step_number,
            "challenge_id": self.challenge_id,
            "answer": self.answer,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "answer_status": self.answer_status,
            "feedback": dict(self.feedback),
            "next_challenge_id": self.next_challenge_id,
            "timestamp": self.timestamp,
            "strategy": None,
            "learner_state": None,
        }


class LinearTutor:
    """Deterministic non-adaptive tutor. Sequence ignores mastery and strategy."""

    def __init__(
        self,
        *,
        sequence: tuple[str, ...] | None = None,
        seed: int = RANDOM_SEED,
    ) -> None:
        self.seed = int(seed)
        self.sequence = sequence or BASELINE_SEQUENCE
        self._index = 0
        self.steps: list[BaselineStep] = []
        self._bank = PHASE3_BY_ID

    @property
    def complete(self) -> bool:
        return self._index >= len(self.sequence)

    def current_challenge(self) -> Challenge | None:
        if self.complete:
            return None
        return self._bank[self.sequence[self._index]]

    def submit(
        self,
        *,
        answer: str,
        confidence: str | LearnerConfidence = LearnerConfidence.UNKNOWN,
        reasoning: str | None = None,
        challenge_id: str | None = None,
        learner_id: str = "baseline-learner",
    ) -> BaselineStep:
        if self.complete:
            raise RuntimeError("baseline session is complete")
        challenge = self.current_challenge()
        assert challenge is not None
        if challenge_id and challenge_id != challenge.challenge_id:
            raise ValueError("challenge_id does not match the current baseline item")
        conf = confidence.value if isinstance(confidence, LearnerConfidence) else str(confidence)
        response = LearnerResponse(
            response_id=f"BL-R-{self._index + 1:03d}",
            learner_id=learner_id,
            concept_id=challenge.concept_id,
            challenge_id=challenge.challenge_id,
            answer=answer,
            reasoning=reasoning,
            learner_confidence=(
                confidence if isinstance(confidence, LearnerConfidence) else LearnerConfidence.UNKNOWN
            ),
        )
        status = classify_answer_status(response, challenge)
        self._index += 1
        nxt = None if self.complete else self.sequence[self._index]
        step = BaselineStep(
            step_number=self._index,
            challenge_id=challenge.challenge_id,
            answer=answer,
            confidence=conf,
            reasoning=reasoning,
            answer_status=status.value,
            feedback=_feedback(status, challenge),
            next_challenge_id=nxt,
            timestamp=_now(),
        )
        self.steps.append(step)
        return step

    def challenge_ids(self) -> tuple[str, ...]:
        return tuple(self.sequence)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "linear_baseline",
            "seed": self.seed,
            "sequence": list(self.sequence),
            "steps": [step.to_dict() for step in self.steps],
            "complete": self.complete,
            "uses_adaptive_tutor": False,
            "uses_learner_state": False,
            "uses_strategy": False,
        }
