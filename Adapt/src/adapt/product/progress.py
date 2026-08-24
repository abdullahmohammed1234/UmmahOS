"""Honest progress views from recorded learner state. No fabricated analytics."""

from __future__ import annotations

from typing import Any

from adapt.content.catalog import CATALOG
from adapt.content.models import ConceptSpec

STATUS_NEW = "new"
STATUS_IN_PROGRESS = "in_progress"
STATUS_PRACTICING = "practicing"
STATUS_STRONG = "strong"
STATUS_NEEDS_ATTENTION = "needs_attention"
STATUS_COMPLETED = "completed"

STATUS_LABELS = {
    STATUS_NEW: "New",
    STATUS_IN_PROGRESS: "In progress",
    STATUS_PRACTICING: "Practicing",
    STATUS_STRONG: "Strong",
    STATUS_NEEDS_ATTENTION: "Needs attention",
    STATUS_COMPLETED: "Completed",
}

HONESTY_LABELS = {
    STATUS_NEW: "Not started",
    STATUS_IN_PROGRESS: "Explored",
    STATUS_PRACTICING: "Building confidence",
    STATUS_STRONG: "Strong evidence",
    STATUS_NEEDS_ATTENTION: "Still uncertain",
    STATUS_COMPLETED: "Strong evidence",
}

PERSISTENCE_NOTE = (
    "Progress shown here is from this visit while ADAPT is running. "
    "It is not a long-term saved learning record, and it is not a claim "
    "that ADAPT improves learning."
)


def derive_status(
    mastery: float | None,
    *,
    attempts: int = 0,
    last_correct: bool | None = None,
) -> str:
    if mastery is None:
        return STATUS_NEW
    value = float(mastery)
    if last_correct is False and value < 0.5:
        return STATUS_NEEDS_ATTENTION
    if value >= 0.85 and attempts >= 2:
        return STATUS_COMPLETED
    if value >= 0.7:
        return STATUS_STRONG
    if attempts >= 2 or 0.45 <= value < 0.7:
        return STATUS_PRACTICING
    if value < 0.4:
        return STATUS_NEEDS_ATTENTION
    return STATUS_IN_PROGRESS


def concept_status_view(
    concept: ConceptSpec,
    *,
    mastery: float | None,
    attempts: int = 0,
    last_correct: bool | None = None,
    recommended: bool = False,
) -> dict[str, Any]:
    status = derive_status(mastery, attempts=attempts, last_correct=last_correct)
    percent = None if mastery is None else int(round(max(0.0, min(1.0, float(mastery))) * 100))
    return {
        **concept.to_dict(mastery=mastery),
        "status": status,
        "status_label": STATUS_LABELS[status],
        "honesty_label": HONESTY_LABELS[status],
        "difficulty_label": {
            "BEGINNER": "Introductory",
            "INTERMEDIATE": "Intermediate",
            "ADVANCED": "Advanced",
        }.get(concept.tier, concept.tier),
        "progress_percent": percent,
        "recommended": recommended,
        "attempts": attempts,
        "action_label": "Continue" if mastery is not None else "Start learning",
    }


def subject_progress_row(
    subject_id: str,
    *,
    concept_mastery: dict[str, float],
    activity: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    subject = CATALOG.subject(subject_id)
    if subject is None:
        return {}
    concepts = CATALOG.concepts_for_subject(subject_id)
    values = [concept_mastery[item.concept_id] for item in concepts if item.concept_id in concept_mastery]
    percent = int(round(sum(values) / len(values) * 100)) if values else None
    started = len(values)
    return {
        **subject.to_dict(concept_count=len(concepts), topic_count=len(subject.topic_ids)),
        "mastery": None if percent is None else round(percent / 100, 4),
        "mastery_percent": percent,
        "progress_available": percent is not None,
        "status_label": "In progress" if started else "New",
        "honesty_label": "Explored" if started else "Not started",
        "action_label": "Continue" if started else "Start",
        "concepts_started": started,
        "concepts_total": len(concepts),
    }


def learner_progress_view(
    *,
    concept_mastery: dict[str, float],
    activity: dict[str, dict[str, Any]] | None = None,
    subject_id: str | None = None,
    session_completed: int = 0,
    session_concepts: list[str] | None = None,
) -> dict[str, Any]:
    activity = activity or {}
    subjects = []
    overall_values: list[float] = []
    started_subjects = 0
    for subject in CATALOG.subjects:
        row = subject_progress_row(
            subject.subject_id,
            concept_mastery=concept_mastery,
            activity=activity,
        )
        if row.get("progress_available"):
            started_subjects += 1
            overall_values.append(float(row["mastery"]))
        topics = []
        for topic in CATALOG.topics_for_subject(subject.subject_id):
            tvals = [concept_mastery[cid] for cid in topic.concept_ids if cid in concept_mastery]
            topics.append(
                topic.to_dict(
                    mastery=sum(tvals) / len(tvals) if tvals else None,
                    challenge_count=len(CATALOG.challenges_for_topic(topic.topic_id)),
                )
            )
        row["topics"] = topics
        subjects.append(row)
    overall = int(round(sum(overall_values) / len(overall_values) * 100)) if overall_values else None
    concept_map = []
    focus = subject_id
    if focus:
        recommended_id = recommend_concept_id(focus, concept_mastery, activity)
        for concept in CATALOG.concepts_for_subject(focus):
            info = activity.get(concept.concept_id) or {}
            concept_map.append(
                concept_status_view(
                    concept,
                    mastery=concept_mastery.get(concept.concept_id),
                    attempts=int(info.get("attempts") or 0),
                    last_correct=info.get("last_correct"),
                    recommended=concept.concept_id == recommended_id,
                )
            )
    attention = [
        item
        for item in concept_map
        if item.get("status") == STATUS_NEEDS_ATTENTION
    ]
    improving = [
        item
        for item in concept_map
        if item.get("status") in {STATUS_STRONG, STATUS_PRACTICING, STATUS_COMPLETED}
    ]
    return {
        "title": "Your progress",
        "overall_percent": overall,
        "overall_available": overall is not None,
        "subjects": subjects,
        "concept_map": concept_map,
        "subjects_explored": started_subjects,
        "concepts_practiced": len(concept_mastery),
        "challenges_completed": sum(int((activity.get(cid) or {}).get("attempts") or 0) for cid in activity)
        or session_completed,
        "session_completed": session_completed,
        "session_concepts": session_concepts or [],
        "areas_needing_attention": attention,
        "areas_improving": improving,
        "scope": "visit_memory",
        "persistence": "in_memory_while_running",
        "disclaimer": PERSISTENCE_NOTE,
    }


def recommend_concept_id(
    subject_id: str,
    concept_mastery: dict[str, float],
    activity: dict[str, dict[str, Any]] | None = None,
) -> str | None:
    activity = activity or {}
    concepts = CATALOG.concepts_for_subject(subject_id)
    if not concepts:
        return None
    ranked: list[tuple[int, ConceptSpec]] = []
    for concept in concepts:
        mastery = concept_mastery.get(concept.concept_id)
        info = activity.get(concept.concept_id) or {}
        status = derive_status(
            mastery,
            attempts=int(info.get("attempts") or 0),
            last_correct=info.get("last_correct"),
        )
        if status == STATUS_NEEDS_ATTENTION:
            ranked.append((0, concept))
        elif status == STATUS_IN_PROGRESS:
            ranked.append((1, concept))
        elif status == STATUS_PRACTICING:
            ranked.append((2, concept))
        elif status == STATUS_NEW:
            ranked.append((3, concept))
        else:
            ranked.append((4, concept))
    ranked.sort(key=lambda item: item[0])
    return ranked[0][1].concept_id
