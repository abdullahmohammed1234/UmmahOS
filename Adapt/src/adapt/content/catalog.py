"""UmmahOS Community Safety challenge catalog.

Content is aligned with Community Shield learning patterns and Academy
adaptive practice. Only community-safety scenarios are exposed.
"""

from __future__ import annotations

from adapt.content.domains import community_safety
from adapt.content.models import CatalogChallenge, ConceptSpec, Subject, TopicSpec

_DOMAIN_MODULES = (community_safety,)

SUBJECTS: tuple[Subject, ...] = (
    Subject(
        "community-safety",
        "Community Safety",
        "🛡",
        "Context awareness, evidence preservation, and safe reporting for UmmahOS communities.",
        tuple(t.topic_id for t in community_safety.TOPICS),
    ),
)


def _assemble() -> tuple[tuple[Subject, ...], tuple[TopicSpec, ...], tuple[ConceptSpec, ...], tuple[CatalogChallenge, ...]]:
    topics: list[TopicSpec] = []
    concepts: list[ConceptSpec] = []
    challenges: list[CatalogChallenge] = []
    seen_ids: set[str] = set()
    for module in _DOMAIN_MODULES:
        topics.extend(module.TOPICS)
        concepts.extend(module.CONCEPTS)
        for item in module.CHALLENGES:
            if item.id in seen_ids:
                raise ValueError(f"duplicate challenge id: {item.id}")
            seen_ids.add(item.id)
            challenges.append(item)
    subjects = tuple(
        Subject(
            subject_id=spec.subject_id,
            name=spec.name,
            icon=spec.icon,
            blurb=spec.blurb,
            topic_ids=tuple(t.topic_id for t in topics if t.subject_id == spec.subject_id),
        )
        for spec in SUBJECTS
    )
    return subjects, tuple(topics), tuple(concepts), tuple(challenges)


class ChallengeCatalog:
    def __init__(self) -> None:
        subjects, topics, concepts, challenges = _assemble()
        self.subjects = subjects
        self.topics = topics
        self.concepts = concepts
        self.challenges = challenges
        self._subjects = {item.subject_id: item for item in subjects}
        self._topics = {item.topic_id: item for item in topics}
        self._concepts = {item.concept_id: item for item in concepts}
        self._challenges = {item.id: item for item in challenges}
        self.engine_bank = tuple(item.to_engine() for item in challenges)
        self._engine_by_id = {item.challenge_id: item for item in self.engine_bank}

    def subject(self, subject_id: str) -> Subject | None:
        return self._subjects.get(subject_id)

    def topic(self, topic_id: str) -> TopicSpec | None:
        return self._topics.get(topic_id)

    def concept(self, concept_id: str) -> ConceptSpec | None:
        return self._concepts.get(concept_id)

    def challenge(self, challenge_id: str) -> CatalogChallenge | None:
        return self._challenges.get(challenge_id)

    def engine_challenge(self, challenge_id: str):
        return self._engine_by_id.get(challenge_id)

    def topics_for_subject(self, subject_id: str) -> tuple[TopicSpec, ...]:
        return tuple(item for item in self.topics if item.subject_id == subject_id)

    def concepts_for_topic(self, topic_id: str) -> tuple[ConceptSpec, ...]:
        return tuple(item for item in self.concepts if item.topic_id == topic_id)

    def concepts_for_subject(self, subject_id: str) -> tuple[ConceptSpec, ...]:
        return tuple(item for item in self.concepts if item.subject_id == subject_id)

    def challenges_for_topic(self, topic_id: str) -> tuple[CatalogChallenge, ...]:
        return tuple(item for item in self.challenges if item.topic_id == topic_id)

    def challenges_for_concept(self, concept_id: str) -> tuple[CatalogChallenge, ...]:
        return tuple(item for item in self.challenges if item.concept_id == concept_id)

    def family_id(self, challenge_id: str) -> str:
        item = self._challenges.get(challenge_id)
        return item.family if item else challenge_id

    def concept_label(self, concept_id: str) -> str:
        item = self._concepts.get(concept_id)
        if item is not None:
            return item.name
        topic = next((row for row in self.topics if concept_id in row.concept_ids), None)
        if topic is not None:
            return topic.name
        return concept_id

    def list_subjects(self) -> list[dict]:
        out = []
        for subject in self.subjects:
            concepts = self.concepts_for_subject(subject.subject_id)
            out.append(subject.to_dict(concept_count=len(concepts), topic_count=len(subject.topic_ids)))
        return out

    def validate(self) -> list[str]:
        errors: list[str] = []
        topic_ids = {item.topic_id for item in self.topics}
        concept_ids = {item.concept_id for item in self.concepts}
        for subject in self.subjects:
            if not subject.topic_ids:
                errors.append(f"subject {subject.subject_id} has no topics")
            for topic_id in subject.topic_ids:
                if topic_id not in topic_ids:
                    errors.append(f"subject {subject.subject_id} missing topic {topic_id}")
        for topic in self.topics:
            if topic.subject_id not in self._subjects:
                errors.append(f"topic {topic.topic_id} has unknown subject")
            if not topic.concept_ids:
                errors.append(f"topic {topic.topic_id} has no concepts")
            for concept_id in topic.concept_ids:
                if concept_id not in concept_ids:
                    errors.append(f"topic {topic.topic_id} missing concept {concept_id}")
            if not self.challenges_for_topic(topic.topic_id) and not topic.legacy:
                errors.append(f"topic {topic.topic_id} has no challenges")
        for concept in self.concepts:
            if concept.topic_id not in topic_ids:
                errors.append(f"concept {concept.concept_id} has unknown topic")
        for item in self.challenges:
            if item.concept_id not in concept_ids:
                errors.append(f"challenge {item.id} references unknown concept {item.concept_id}")
            if item.topic_id not in topic_ids:
                errors.append(f"challenge {item.id} references unknown topic {item.topic_id}")
            if not str(item.answer).strip():
                errors.append(f"challenge {item.id} has empty answer")
        ids = [item.id for item in self.challenges]
        if len(ids) != len(set(ids)):
            errors.append("challenge ids are not unique")
        return errors

    def metrics(self) -> dict[str, int]:
        types = {item.challenge_type for item in self.challenges}
        return {
            "subjects": len(self.subjects),
            "topics": len(self.topics),
            "concepts": len(self.concepts),
            "challenges": len(self.challenges),
            "challenge_types": len(types),
        }


CATALOG = ChallengeCatalog()
