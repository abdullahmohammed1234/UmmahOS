from adapt.content.catalog import CATALOG
from adapt.content.types import PRODUCT_CHALLENGE_TYPES


def test_catalog_has_community_safety_subject():
    assert len(CATALOG.subjects) == 1
    ids = {item.subject_id for item in CATALOG.subjects}
    assert ids == {"community-safety"}


def test_catalog_validate_is_clean():
    assert CATALOG.validate() == []


def test_every_subject_has_topics():
    for subject in CATALOG.subjects:
        topics = CATALOG.topics_for_subject(subject.subject_id)
        assert topics, subject.subject_id


def test_every_topic_has_concepts():
    for topic in CATALOG.topics:
        assert topic.concept_ids
        for concept_id in topic.concept_ids:
            assert CATALOG.concept(concept_id) is not None, concept_id


def test_every_challenge_references_valid_concept_and_has_answer():
    ids = [item.id for item in CATALOG.challenges]
    assert len(ids) == len(set(ids))
    for item in CATALOG.challenges:
        assert CATALOG.concept(item.concept_id) is not None, item.id
        assert str(item.answer).strip(), item.id
        assert item.challenge_type in PRODUCT_CHALLENGE_TYPES


def test_concept_and_type_coverage():
    metrics = CATALOG.metrics()
    assert metrics["concepts"] >= 12
    assert metrics["challenge_types"] >= 4
    types = {item.challenge_type for item in CATALOG.challenges}
    assert {"SCENARIO", "ERROR_ANALYSIS", "CONCEPT_CHECK", "APPLICATION"} & types


def test_community_safety_misconceptions_are_tagged():
    challenges = [item for item in CATALOG.challenges if item.domain == "community-safety"]
    tags = {tag for item in challenges for tag in item.misconception_tags}
    for code in ("CSAFE-M001", "CSAFE-M002", "CSAFE-M003", "CSAFE-M004", "CSAFE-M005"):
        assert code in tags, code


def test_ummahos_seed_challenges_present():
    assert CATALOG.challenge("CSAFE-CTX-001") is not None
    assert CATALOG.challenge("CSAFE-CTX-001").topic_id == "csafety-context"
