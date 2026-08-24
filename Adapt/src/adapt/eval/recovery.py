"""Misconception recovery using Phase 1–3 evidence standards.

A single lucky correct answer is not recovery. Recovery requires:
1. Prior misconception evidence on a targeted training item
2. Later correct response on an equivalent item
3. Conceptual reasoning cues on that later response
"""

from __future__ import annotations

from typing import Any

from adapt.analysis.evidence_analyzer import classify_answer_status, classify_reasoning_quality
from adapt.eval.constants import (
    ADD_DENOM,
    ADD_DENOM_POST_IDS,
    ADD_DENOM_TRAINING_IDS,
    CONCEPTUAL_CUES,
    DIST_PROP,
    DIST_PROP_POST_IDS,
    DIST_PROP_TRAINING_IDS,
)
from adapt.eval.materials import AssessmentItem, items_by_id
from adapt.models.enums import AnswerStatus, ReasoningQuality
from adapt.models.learner_response import LearnerResponse
from adapt.tutor.challenge_bank import PHASE3_BY_ID

SCENARIOS = (
    {
        "id": "MR-DIST-PROP",
        "misconception": DIST_PROP,
        "training_ids": DIST_PROP_TRAINING_IDS,
        "post_ids": DIST_PROP_POST_IDS,
    },
    {
        "id": "MR-ADD-DENOM",
        "misconception": ADD_DENOM,
        "training_ids": ADD_DENOM_TRAINING_IDS,
        "post_ids": ADD_DENOM_POST_IDS,
    },
)


def _has_cue(text: str | None, cues: tuple[str, ...]) -> bool:
    if not text:
        return False
    lowered = text.lower()
    return any(cue.lower() in lowered for cue in cues)


def _training_misconception(step: dict[str, Any], misconception: str, training_ids: frozenset[str]) -> bool:
    challenge_id = step.get("challenge_id")
    if challenge_id not in training_ids:
        return False
    evidence = step.get("evidence") or {}
    if evidence.get("misconception_signal") == misconception:
        return True
    answer = str(step.get("answer") or "")
    reasoning = step.get("reasoning")
    combined = f"{answer} {reasoning or ''}".lower()
    if misconception == DIST_PROP and any(cue in combined for cue in ("2x+3", "2x + 3", "didn't distribute", "did not distribute")):
        if (step.get("answer_status") or evidence.get("answer_status")) in {"INCORRECT", "PARTIAL"}:
            return True
    if misconception == ADD_DENOM and any(cue in combined for cue in ("2/5", "add the denominators", "add tops and bottoms")):
        if (step.get("answer_status") or evidence.get("answer_status")) in {"INCORRECT", "PARTIAL"}:
            return True
    return False


def _post_conceptual_correct(
    item: AssessmentItem,
    answer: str | None,
    reasoning: str | None,
    misconception: str,
) -> bool:
    if not answer:
        return False
    response = LearnerResponse(
        response_id=f"rec-{item.item_id}",
        learner_id="recovery",
        concept_id=item.concept,
        challenge_id=item.item_id,
        answer=answer,
        reasoning=reasoning,
    )
    challenge = item.as_challenge()
    status = classify_answer_status(response, challenge)
    if status != AnswerStatus.CORRECT:
        return False
    quality = classify_reasoning_quality(response, challenge)
    if quality == ReasoningQuality.STRONG:
        return True
    if quality == ReasoningQuality.MODERATE and _has_cue(reasoning, CONCEPTUAL_CUES[misconception]):
        return True
    return False


def evaluate_recovery(
    *,
    training_steps: list[dict[str, Any]],
    post_items: list[dict[str, Any]],
    post_form: tuple[AssessmentItem, ...] | None = None,
) -> dict[str, Any]:
    catalog = items_by_id()
    results = []
    recovered = 0
    applicable = 0
    for spec in SCENARIOS:
        shown = any(
            _training_misconception(step, spec["misconception"], spec["training_ids"])
            for step in training_steps
        )
        later = None
        for row in post_items:
            item_id = row.get("item_id")
            if item_id in spec["post_ids"]:
                later = row
                break
        if not shown:
            results.append(
                {
                    "scenario_id": spec["id"],
                    "misconception": spec["misconception"],
                    "status": "NOT_APPLICABLE",
                    "recovered": None,
                    "reason": "misconception was not observed during training",
                }
            )
            continue
        applicable += 1
        if later is None:
            results.append(
                {
                    "scenario_id": spec["id"],
                    "misconception": spec["misconception"],
                    "status": "NOT_RECOVERED",
                    "recovered": 0,
                    "reason": "no equivalent post-test item was answered",
                }
            )
            continue
        item = catalog.get(later["item_id"])
        if item is None and post_form:
            item = next((entry for entry in post_form if entry.item_id == later["item_id"]), None)
        if item is None:
            results.append(
                {
                    "scenario_id": spec["id"],
                    "misconception": spec["misconception"],
                    "status": "NOT_RECOVERED",
                    "recovered": 0,
                    "reason": "post-test item is unknown",
                }
            )
            continue
        ok = _post_conceptual_correct(
            item,
            later.get("answer"),
            later.get("reasoning"),
            spec["misconception"],
        )
        if ok:
            recovered += 1
            status = "RECOVERED"
            reason = "later equivalent item was correct with conceptual reasoning"
        else:
            status = "NOT_RECOVERED"
            reason = "later item was missing, incorrect, or lacked conceptual reasoning"
        results.append(
            {
                "scenario_id": spec["id"],
                "misconception": spec["misconception"],
                "status": status,
                "recovered": 1 if ok else 0,
                "reason": reason,
            }
        )
    rate = None if applicable == 0 else recovered / applicable
    return {
        "scenarios": results,
        "applicable": applicable,
        "recovered": recovered,
        "rate": rate,
    }


def challenge_from_bank(challenge_id: str):
    return PHASE3_BY_ID.get(challenge_id)
