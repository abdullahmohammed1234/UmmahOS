"""Product-layer study suggestions from recorded progress and last strategy.

Not a second adaptive engine. Strategy labels come from recorded AdaptiveTutor
decisions when available.
"""

from __future__ import annotations

from typing import Any

from adapt.content.catalog import CATALOG
from adapt.product.progress import concept_status_view, recommend_concept_id


def recommend_for_subject(
    subject_id: str,
    *,
    concept_mastery: dict[str, float],
    activity: dict[str, dict[str, Any]] | None = None,
    last_strategy: str | None = None,
    current_concept_id: str | None = None,
) -> dict[str, Any] | None:
    concept_id = recommend_concept_id(subject_id, concept_mastery, activity)
    if concept_id is None:
        return None
    concept = CATALOG.concept(concept_id)
    if concept is None:
        return None
    info = (activity or {}).get(concept_id) or {}
    view = concept_status_view(
        concept,
        mastery=concept_mastery.get(concept_id),
        attempts=int(info.get("attempts") or 0),
        last_correct=info.get("last_correct"),
        recommended=True,
    )
    view["source"] = "recorded_progress"
    view["engine_decision"] = False
    view["items"] = recommendation_items(
        subject_id,
        concept_mastery=concept_mastery,
        activity=activity or {},
        last_strategy=last_strategy or info.get("last_strategy"),
        current_concept_id=current_concept_id or concept_id,
        primary=view,
    )
    return view


def recommendation_items(
    subject_id: str,
    *,
    concept_mastery: dict[str, float],
    activity: dict[str, dict[str, Any]],
    last_strategy: str | None,
    current_concept_id: str | None,
    primary: dict[str, Any],
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    if current_concept_id:
        current = CATALOG.concept(current_concept_id)
        if current is not None:
            items.append(
                {
                    "kind": "continue",
                    "label": "Continue current concept",
                    "concept_id": current.concept_id,
                    "name": current.name,
                    "source": "recorded_progress",
                }
            )
    last = str(last_strategy or "")
    if last == "REMEDIATE" or primary.get("status") == "needs_attention":
        items.append(
            {
                "kind": "review",
                "label": "Review a mix-up",
                "concept_id": primary.get("concept_id"),
                "name": primary.get("name"),
                "source": "recorded_strategy" if last == "REMEDIATE" else "recorded_progress",
            }
        )
    related = next(
        (
            item
            for item in CATALOG.concepts_for_subject(subject_id)
            if item.concept_id != current_concept_id and item.concept_id not in concept_mastery
        ),
        None,
    )
    if related is not None:
        items.append(
            {
                "kind": "related",
                "label": "Try a related concept",
                "concept_id": related.concept_id,
                "name": related.name,
                "source": "catalog",
            }
        )
    if last == "INCREASE":
        items.append(
            {
                "kind": "increase",
                "label": "Increase challenge",
                "concept_id": current_concept_id,
                "source": "recorded_strategy",
                "strategy": last,
            }
        )
    other = next((item for item in CATALOG.subjects if item.subject_id != subject_id), None)
    if other is not None:
        items.append(
            {
                "kind": "explore",
                "label": "Explore another domain",
                "subject_id": other.subject_id,
                "name": other.name,
                "source": "catalog",
            }
        )
    return items
