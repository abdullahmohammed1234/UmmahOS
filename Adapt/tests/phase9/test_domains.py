"""Community Safety catalog coverage for UmmahOS."""

from adapt.content.catalog import CATALOG
from adapt.content.types import PRODUCT_CHALLENGE_TYPES


REQUIRED_SUBJECTS = {"community-safety"}

REQUIRED_CONCEPTS = {
    "csafety_context_preservation",
    "csafety_pattern_recognition",
    "csafety_safe_reporting",
    "csafety_evidence_quality",
    "csafety_uncertainty",
    "csafety_coded_recognition",
    "csafety_repeated_targeting",
    "csafety_report_channels",
    "csafety_reporter_privacy",
}


def test_community_safety_subject_only():
    ids = {item.subject_id for item in CATALOG.subjects}
    assert ids == REQUIRED_SUBJECTS
    assert CATALOG.validate() == []


def test_community_safety_concept_coverage():
    concept_ids = {item.concept_id for item in CATALOG.concepts}
    assert REQUIRED_CONCEPTS <= concept_ids
    assert len(CATALOG.concepts) >= 10
    for concept in CATALOG.concepts:
        bank = CATALOG.challenges_for_concept(concept.concept_id)
        assert bank, concept.concept_id


def test_community_safety_challenge_types():
    types = {item.challenge_type for item in CATALOG.challenges}
    assert "SCENARIO" in types
    assert types <= set(PRODUCT_CHALLENGE_TYPES)
    tags = {tag for item in CATALOG.challenges for tag in item.misconception_tags}
    for code in ("CSAFE-M001", "CSAFE-M002", "CSAFE-M003"):
        assert code in tags
