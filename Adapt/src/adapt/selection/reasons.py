"""Selection reasons derived from the ranking, not hardcoded copy."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from adapt.content.models import CatalogChallenge
from adapt.models.enums import StrategyName


@dataclass(frozen=True)
class SelectionResult:
    challenge: CatalogChallenge
    strategy: StrategyName
    reasons: tuple[str, ...]
    scores: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "challenge_id": self.challenge.id,
            "strategy": self.strategy.value,
            "reasons": list(self.reasons),
            "scores": dict(self.scores),
            "challenge_type": self.challenge.challenge_type,
            "difficulty": self.challenge.difficulty,
            "family_id": self.challenge.family,
        }


def learner_why(strategy: StrategyName, reasons: tuple[str, ...], *, evidence_notes: tuple[str, ...] = ()) -> str:
    joined = " ".join(reasons)
    if strategy == StrategyName.INCREASE:
        return (
            "You solved the previous problem with strong evidence, so ADAPT increased "
            "the challenge to test whether you can apply the same idea in a new situation."
        )
    if strategy == StrategyName.PROBE:
        if "low_confidence" in evidence_notes or "weak_reasoning" in joined:
            return (
                "Your answer was correct, but your confidence or reasoning was uncertain. "
                "ADAPT chose a different question to check whether you really understand the concept."
            )
        return (
            "ADAPT is checking this concept another way before deciding whether to move ahead."
        )
    if strategy == StrategyName.REMEDIATE:
        return (
            "ADAPT noticed the same mix-up more than once, so this question is designed to help address it."
        )
    if strategy == StrategyName.DECREASE:
        return "Recent evidence suggested this level was too hard, so ADAPT stepped back to rebuild the idea."
    if strategy == StrategyName.GATHER_EVIDENCE:
        return "ADAPT still needs a bit more evidence before making a bigger change, so this is another observation."
    if strategy == StrategyName.ASSESS:
        return "ADAPT is still getting a first picture of how you approach this topic."
    if strategy == StrategyName.RECOVER:
        return "Your recent responses improved, so ADAPT is moving you forward from the extra-support path."
    if "diversity" in joined:
        return "Several questions fit the current plan, so ADAPT picked a different style so practice does not feel like a worksheet."
    return "ADAPT chose this challenge because it matches the current instructional plan for this concept."
