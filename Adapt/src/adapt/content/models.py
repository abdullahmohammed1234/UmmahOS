"""Domain-neutral product content models. Independent of the frozen engine Challenge."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from adapt.content.types import (
    DEFAULT_STRATEGY_FIT,
    PRODUCT_CHALLENGE_TYPES,
    engine_difficulty_to_product,
    engine_type_for_product,
    engine_type_to_product,
    product_difficulty_to_engine,
)
from adapt.models.challenge import Challenge


@dataclass(frozen=True)
class Subject:
    subject_id: str
    name: str
    icon: str
    blurb: str
    topic_ids: tuple[str, ...]

    def to_dict(self, *, concept_count: int = 0, topic_count: int = 0) -> dict[str, Any]:
        return {
            "subject_id": self.subject_id,
            "name": self.name,
            "icon": self.icon,
            "blurb": self.blurb,
            "topic_ids": list(self.topic_ids),
            "concept_count": concept_count,
            "topic_count": topic_count or len(self.topic_ids),
        }


@dataclass(frozen=True)
class TopicSpec:
    topic_id: str
    subject_id: str
    name: str
    description: str
    concept_ids: tuple[str, ...]
    initial_challenge: str
    legacy: bool = False

    def as_topic(self):
        from adapt.product.topics import Topic

        primary = self.concept_ids[0] if self.concept_ids else self.topic_id
        return Topic(
            topic_id=self.topic_id,
            concept_id=primary,
            name=self.name,
            description=self.description,
            initial_challenge=self.initial_challenge,
        )

    def to_dict(self, *, mastery: float | None = None, challenge_count: int = 0) -> dict[str, Any]:
        payload = {
            "topic_id": self.topic_id,
            "subject_id": self.subject_id,
            "name": self.name,
            "description": self.description,
            "concept_ids": list(self.concept_ids),
            "initial_challenge": self.initial_challenge,
            "legacy": self.legacy,
            "challenge_count": challenge_count,
        }
        if mastery is None:
            payload["mastery"] = None
            payload["status"] = "not_started"
        else:
            payload["mastery"] = round(float(mastery), 4)
            payload["status"] = "in_progress"
        return payload


@dataclass(frozen=True)
class ConceptSpec:
    concept_id: str
    topic_id: str
    subject_id: str
    name: str
    description: str
    tier: str = "BEGINNER"

    def to_dict(self, *, mastery: float | None = None) -> dict[str, Any]:
        return {
            "concept_id": self.concept_id,
            "topic_id": self.topic_id,
            "subject_id": self.subject_id,
            "name": self.name,
            "description": self.description,
            "tier": self.tier,
            "mastery": None if mastery is None else round(float(mastery), 4),
        }


@dataclass(frozen=True)
class CatalogChallenge:
    id: str
    domain: str
    topic_id: str
    concept_id: str
    difficulty: int
    challenge_type: str
    prompt: str
    answer: str
    explanation: str
    misconception_tags: tuple[str, ...] = ()
    evidence_requirements: tuple[str, ...] = ("answer", "confidence")
    prerequisites: tuple[str, ...] = ()
    family_id: str = ""
    choices: tuple[str, ...] = ()
    hint: str | None = None
    representation: str = "symbolic"
    reasoning_cues: tuple[str, ...] = ()
    method_cues: tuple[str, ...] = ()
    misconception_cues: tuple[tuple[str, tuple[str, ...]], ...] = ()
    target_misconception: str | None = None
    diagnostic_value: float = 0.55
    strategy_compatibility: tuple[str, ...] = ()
    estimated_time: int = 60
    skills: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    alternative_answers: tuple[str, ...] = ()
    solution: str | None = None
    learn_more: str | None = None

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("challenge id is required")
        if not self.prompt:
            raise ValueError(f"{self.id}: prompt is required")
        if self.answer is None or str(self.answer).strip() == "":
            raise ValueError(f"{self.id}: answer is required")
        if self.challenge_type not in PRODUCT_CHALLENGE_TYPES:
            raise ValueError(f"{self.id}: unknown challenge_type {self.challenge_type}")
        if self.difficulty not in {1, 2, 3, 4, 5}:
            raise ValueError(f"{self.id}: difficulty must be 1–5")

    @property
    def family(self) -> str:
        return self.family_id or self.id

    def to_engine(self) -> Challenge:
        strategies = list(self.strategy_compatibility or DEFAULT_STRATEGY_FIT.get(self.challenge_type, ()))
        if self.difficulty >= 4 and "INCREASE" not in strategies:
            strategies.append("INCREASE")
        if self.challenge_type == "REMEDIATION" and "REMEDIATE" not in strategies:
            strategies.append("REMEDIATE")
        return Challenge(
            challenge_id=self.id,
            concept_id=self.concept_id,
            difficulty=product_difficulty_to_engine(self.difficulty),
            question=self.prompt,
            challenge_type=engine_type_for_product(self.challenge_type, difficulty=self.difficulty),
            expected_answer=self.answer,
            expected_reasoning_cues=self.reasoning_cues,
            correct_method_cues=self.method_cues,
            misconception_cues=self.misconception_cues,
            target_misconception=self.target_misconception,
            representation=self.representation,
            diagnostic_value=self.diagnostic_value,
            strategy_compatibility=tuple(strategies),
        )

    def to_dict(self, *, include_answer: bool = False) -> dict[str, Any]:
        payload = {
            "challenge_id": self.id,
            "id": self.id,
            "domain": self.domain,
            "subject_id": self.domain,
            "topic_id": self.topic_id,
            "concept_id": self.concept_id,
            "difficulty": self.difficulty,
            "difficulty_label": DIFFICULTY_LABELS[self.difficulty],
            "challenge_type": self.challenge_type,
            "prompt": self.prompt,
            "choices": list(self.choices),
            "hint": self.hint,
            "representation": self.representation,
            "family_id": self.family,
            "evidence_requirements": list(self.evidence_requirements),
            "estimated_time": self.estimated_time,
            "tags": list(self.tags),
        }
        if include_answer:
            payload["answer"] = self.answer
            payload["explanation"] = self.explanation
            payload["learn_more"] = self.learn_more
            payload["solution"] = self.solution
        return payload

    @classmethod
    def from_engine(
        cls,
        item: Challenge,
        *,
        domain: str,
        topic_id: str,
        explanation: str = "",
    ) -> CatalogChallenge:
        product_type = engine_type_to_product(item.challenge_type)
        return cls(
            id=item.challenge_id,
            domain=domain,
            topic_id=topic_id,
            concept_id=item.concept_id,
            difficulty=engine_difficulty_to_product(item.difficulty),
            challenge_type=product_type,
            prompt=item.question,
            answer=item.expected_answer or "",
            explanation=explanation,
            misconception_tags=tuple(
                mid for mid, _cues in item.misconception_cues
            ),
            family_id=item.challenge_id.rsplit("-", 1)[0] if "-" in item.challenge_id else item.challenge_id,
            representation=item.representation,
            reasoning_cues=item.expected_reasoning_cues,
            method_cues=item.correct_method_cues,
            misconception_cues=item.misconception_cues,
            target_misconception=item.target_misconception,
            diagnostic_value=item.diagnostic_value,
            strategy_compatibility=item.strategy_compatibility,
        )


DIFFICULTY_LABELS = {
    1: "Introductory",
    2: "Basic",
    3: "Intermediate",
    4: "Advanced",
    5: "Challenge",
}


def ch(
    challenge_id: str,
    domain: str,
    topic_id: str,
    concept_id: str,
    difficulty: int,
    challenge_type: str,
    prompt: str,
    answer: str,
    explanation: str,
    *,
    family: str | None = None,
    choices: tuple[str, ...] = (),
    cues: tuple[str, ...] = (),
    methods: tuple[str, ...] = (),
    misconceptions: tuple[tuple[str, tuple[str, ...]], ...] = (),
    tags: tuple[str, ...] = (),
    target: str | None = None,
    hint: str | None = None,
    representation: str = "text",
    diagnostic: float | None = None,
    strategies: tuple[str, ...] = (),
    evidence: tuple[str, ...] = ("answer", "confidence"),
    learn_more: str | None = None,
    prereq: tuple[str, ...] = (),
) -> CatalogChallenge:
    if diagnostic is None:
        diagnostic = {
            "DIAGNOSTIC": 0.9,
            "PREDICTION": 0.86,
            "ERROR_ANALYSIS": 0.88,
            "EXPLANATION": 0.84,
            "COMPARE": 0.82,
            "REMEDIATION": 0.8,
            "TRUE_FALSE": 0.72,
            "TRANSFER": 0.66,
            "APPLICATION": 0.64,
            "SCENARIO": 0.62,
            "NUMERIC": 0.58,
            "SHORT_ANSWER": 0.7,
            "DEBUG": 0.88,
            "MATCH": 0.74,
            "DIAGRAM": 0.68,
            "ESTIMATION": 0.64,
            "EXPLAIN_CHOICE": 0.84,
        }.get(challenge_type, 0.55)
    return CatalogChallenge(
        id=challenge_id,
        domain=domain,
        topic_id=topic_id,
        concept_id=concept_id,
        difficulty=difficulty,
        challenge_type=challenge_type,
        prompt=prompt,
        answer=answer,
        explanation=explanation,
        misconception_tags=tuple(mid for mid, _ in misconceptions) + tags,
        evidence_requirements=evidence,
        prerequisites=prereq,
        family_id=family or challenge_id.rsplit("-", 1)[0],
        choices=choices,
        hint=hint,
        representation=representation,
        reasoning_cues=cues,
        method_cues=methods or cues,
        misconception_cues=misconceptions,
        target_misconception=target or (misconceptions[0][0] if misconceptions else None),
        diagnostic_value=diagnostic,
        strategy_compatibility=strategies,
        tags=tags,
        learn_more=learn_more,
    )
