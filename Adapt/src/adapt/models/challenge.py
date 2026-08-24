"""Minimal challenge representation plus deterministic scoring metadata."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from adapt.errors import InvalidChallengeError
from adapt.models.enums import ChallengeType, Difficulty, parse_enum


@dataclass(frozen=True)
class Challenge:
    challenge_id: str
    concept_id: str
    difficulty: Difficulty
    question: str
    challenge_type: ChallengeType
    expected_answer: str | None = None
    expected_reasoning_cues: tuple[str, ...] = ()
    correct_method_cues: tuple[str, ...] = ()
    misconception_cues: tuple[tuple[str, tuple[str, ...]], ...] = ()
    target_misconception: str | None = None
    representation: str = "symbolic"
    diagnostic_value: float = 0.5
    strategy_compatibility: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.challenge_id:
            raise InvalidChallengeError("challenge_id is required")
        if not self.concept_id:
            raise InvalidChallengeError("concept_id is required")
        if not self.question:
            raise InvalidChallengeError("question is required")
        if not isinstance(self.diagnostic_value, (int, float)) or isinstance(
            self.diagnostic_value, bool
        ):
            raise InvalidChallengeError("diagnostic_value must be a number")
        if not 0.0 <= float(self.diagnostic_value) <= 1.0:
            raise InvalidChallengeError("diagnostic_value must be in [0, 1]")

    def compatible_with(self, strategy_name: str) -> bool:
        if not self.strategy_compatibility:
            return True
        return strategy_name in self.strategy_compatibility

    def to_dict(self) -> dict[str, Any]:
        return {
            "challenge_id": self.challenge_id,
            "concept_id": self.concept_id,
            "difficulty": self.difficulty.value,
            "question": self.question,
            "challenge_type": self.challenge_type.value,
            "expected_answer": self.expected_answer,
            "expected_reasoning_cues": list(self.expected_reasoning_cues),
            "correct_method_cues": list(self.correct_method_cues),
            "misconception_cues": [
                {"misconception_id": mid, "cues": list(cues)}
                for mid, cues in self.misconception_cues
            ],
            "target_misconception": self.target_misconception,
            "representation": self.representation,
            "diagnostic_value": round(float(self.diagnostic_value), 4),
            "strategy_compatibility": list(self.strategy_compatibility),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Challenge:
        if not isinstance(data, dict):
            raise InvalidChallengeError("challenge must be an object")
        try:
            raw_misc = data.get("misconception_cues") or []
            misconception_cues: list[tuple[str, tuple[str, ...]]] = []
            for item in raw_misc:
                if isinstance(item, dict):
                    misconception_cues.append(
                        (item["misconception_id"], tuple(item.get("cues") or []))
                    )
                else:
                    raise InvalidChallengeError("malformed misconception_cues")
            return cls(
                challenge_id=data["challenge_id"],
                concept_id=data["concept_id"],
                difficulty=parse_enum(
                    data["difficulty"],
                    Difficulty,
                    field_name="difficulty",
                    error_cls=InvalidChallengeError,
                ),
                question=data["question"],
                challenge_type=parse_enum(
                    data["challenge_type"],
                    ChallengeType,
                    field_name="challenge_type",
                    error_cls=InvalidChallengeError,
                ),
                expected_answer=data.get("expected_answer"),
                expected_reasoning_cues=tuple(data.get("expected_reasoning_cues") or []),
                correct_method_cues=tuple(data.get("correct_method_cues") or []),
                misconception_cues=tuple(misconception_cues),
                target_misconception=data.get("target_misconception"),
                representation=data.get("representation", "symbolic"),
                diagnostic_value=float(data.get("diagnostic_value", 0.5)),
                strategy_compatibility=tuple(data.get("strategy_compatibility") or ()),
            )
        except KeyError as exc:
            raise InvalidChallengeError(f"Missing challenge field: {exc}") from exc
