"""Domain-specific presentation metadata. Does not affect adaptive decisions."""

from __future__ import annotations

from typing import Any

from adapt.content.catalog import CATALOG
from adapt.content.models import CatalogChallenge

SUBJECT_THEMES = {
    "community-safety": {
        "theme": "community-safety",
        "label": "Community Safety",
        "blurb": "Context awareness, evidence preservation, and safe reporting.",
        "visual": "shield",
    },
}

CONCEPT_VISUALS = {
    "csafety_context_preservation": "context",
    "csafety_pattern_recognition": "pattern",
    "csafety_safe_reporting": "report",
    "csafety_evidence_quality": "evidence",
    "csafety_uncertainty": "uncertainty",
    "csafety_coded_recognition": "coded",
    "csafety_dog_whistles": "coded",
    "csafety_neutral_tone": "tone",
    "csafety_repeated_targeting": "pattern",
    "csafety_escalation_signs": "escalation",
    "csafety_bystander_role": "bystander",
    "csafety_report_channels": "report",
    "csafety_escalation_timing": "urgent",
    "csafety_documentation": "evidence",
    "csafety_reporter_privacy": "privacy",
    "csafety_need_to_know": "privacy",
}


def display_prompt(text: str) -> str:
    return str(text or "")


def subject_theme(subject_id: str | None) -> dict[str, Any]:
    if not subject_id:
        return {"theme": "default", "label": "ADAPT", "blurb": "", "visual": "none"}
    return dict(SUBJECT_THEMES.get(subject_id, {"theme": "default", "label": subject_id, "blurb": "", "visual": "none"}))


def visual_for_concept(concept_id: str, subject_id: str | None = None) -> str:
    if concept_id in CONCEPT_VISUALS:
        return CONCEPT_VISUALS[concept_id]
    theme = subject_theme(subject_id)
    return str(theme.get("visual") or "none")


def challenge_presentation(
    challenge_id: str | None,
    *,
    subject_id: str | None = None,
) -> dict[str, Any]:
    meta: CatalogChallenge | None = CATALOG.challenge(challenge_id) if challenge_id else None
    domain = subject_id or (meta.domain if meta else None)
    theme = subject_theme(domain)
    concept_id = meta.concept_id if meta else ""
    visual = visual_for_concept(concept_id, domain)
    prompt = display_prompt(meta.prompt if meta else "")
    return {
        "theme": theme["theme"],
        "subject_id": domain,
        "visual": visual,
        "prompt_display": prompt,
        "code_like": False,
        "representation": meta.representation if meta else "text",
        "challenge_type": meta.challenge_type if meta else None,
        "concept_id": concept_id,
    }
