"""Supported learner topics for legacy core runtime sessions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from adapt.product.errors import InvalidResponseError


@dataclass(frozen=True)
class Topic:
    topic_id: str
    concept_id: str
    name: str
    description: str
    initial_challenge: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "topic_id": self.topic_id,
            "concept_id": self.concept_id,
            "name": self.name,
            "description": self.description,
            "initial_challenge": self.initial_challenge,
        }


# Legacy Phase 3 algebra/fractions topics remain for internal engine tests only.
ALGEBRA = Topic(
    topic_id="algebra",
    concept_id="basic_algebra",
    name="Algebra",
    description="Solve equations and reason about expressions.",
    initial_challenge="ALG-D-001",
)

FRACTIONS = Topic(
    topic_id="fractions",
    concept_id="fractions",
    name="Fractions",
    description="Add, subtract, and reason about parts of a whole.",
    initial_challenge="FR-D-001",
)

TOPICS: tuple[Topic, ...] = (ALGEBRA, FRACTIONS)
TOPICS_BY_ID = {item.topic_id: item for item in TOPICS}
TOPICS_BY_CONCEPT = {item.concept_id: item for item in TOPICS}

CONCEPT_LABELS = {
    "basic_algebra": "Algebraic equations",
    "fractions": "Fractions",
}


def list_topics() -> list[dict[str, Any]]:
    return [item.to_dict() for item in TOPICS]


def require_topic(topic_id: str) -> Topic:
    topic = TOPICS_BY_ID.get(topic_id)
    if topic is None:
        raise InvalidResponseError(f"unsupported topic: {topic_id}")
    return topic


def topic_for_concept(concept_id: str) -> Topic | None:
    return TOPICS_BY_CONCEPT.get(concept_id)
