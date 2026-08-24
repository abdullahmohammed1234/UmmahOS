"""Challenge history for product-layer selection. Does not update mastery."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ChallengeAttempt:
    challenge_id: str
    session_id: str
    sequence: int
    concept_id: str
    difficulty: int
    challenge_type: str
    family_id: str
    result: str
    strategy: str
    used_for_remediation: bool = False
    used_as_diagnostic: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "challenge_id": self.challenge_id,
            "session_id": self.session_id,
            "sequence": self.sequence,
            "concept_id": self.concept_id,
            "difficulty": self.difficulty,
            "challenge_type": self.challenge_type,
            "family_id": self.family_id,
            "result": self.result,
            "strategy": self.strategy,
            "used_for_remediation": self.used_for_remediation,
            "used_as_diagnostic": self.used_as_diagnostic,
        }


@dataclass
class ChallengeHistory:
    attempts: list[ChallengeAttempt] = field(default_factory=list)

    def record(self, attempt: ChallengeAttempt) -> None:
        self.attempts.append(attempt)

    def ids(self) -> list[str]:
        return [item.challenge_id for item in self.attempts]

    def recent(self, window: int = 3) -> list[ChallengeAttempt]:
        if window <= 0:
            return []
        return list(self.attempts[-window:])

    def recently_seen(self, challenge_id: str, *, window: int = 8) -> bool:
        return any(item.challenge_id == challenge_id for item in self.recent(window))

    def family_recent(self, family_id: str, *, window: int = 4) -> bool:
        return any(item.family_id == family_id for item in self.recent(window))

    def count(self, challenge_id: str) -> int:
        return sum(1 for item in self.attempts if item.challenge_id == challenge_id)

    def previously_failed(self, challenge_id: str) -> bool:
        return any(
            item.challenge_id == challenge_id and item.result in {"incorrect", "partial"}
            for item in self.attempts
        )

    def previously_mastered(self, challenge_id: str) -> bool:
        return any(
            item.challenge_id == challenge_id and item.result == "correct"
            for item in self.attempts
        )

    def types(self) -> list[str]:
        return [item.challenge_type for item in self.attempts]

    def from_used_ids(self, used_ids: list[str], *, lookup) -> None:
        """Rebuild a lightweight history from used challenge ids when traces are unavailable."""
        if self.attempts:
            return
        for index, challenge_id in enumerate(used_ids):
            meta = lookup(challenge_id)
            if meta is None:
                continue
            self.attempts.append(
                ChallengeAttempt(
                    challenge_id=challenge_id,
                    session_id="",
                    sequence=index,
                    concept_id=meta.concept_id,
                    difficulty=meta.difficulty,
                    challenge_type=meta.challenge_type,
                    family_id=meta.family,
                    result="unknown",
                    strategy="UNKNOWN",
                )
            )

    def to_dict(self) -> dict[str, Any]:
        return {"attempts": [item.to_dict() for item in self.attempts]}
