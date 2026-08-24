"""Run ADAPT (via ProductService → AdaptiveTutor) and the linear baseline."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from adapt.eval.baseline import LinearTutor
from adapt.eval.constants import (
    ADAPT_START,
    TRAINING_STEPS_PER_TOPIC,
    TOPICS,
)
from adapt.eval.materials import POSTTEST_BY_CONDITION, PRETEST, AssessmentItem
from adapt.eval.recovery import evaluate_recovery
from adapt.eval.scoring import learning_gain, score_test
from adapt.eval.survey import parse_survey
from adapt.models.enums import LearnerConfidence
from adapt.product.service import ProductService
from adapt.tutor.tutor import AdaptiveTutor, DEFAULT_SEED


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _confidence(value: Any) -> Any:
    if value is None:
        return 3
    return value


def score_form(form: tuple[AssessmentItem, ...], answers: dict[str, Any] | None) -> dict[str, Any]:
    payload = score_test(form, None if answers is None else answers)
    payload["timestamp"] = _now()
    payload["responses"] = []
    if answers:
        for item in form:
            payload["responses"].append(
                {
                    "item_id": item.item_id,
                    "answer": answers.get(item.item_id),
                    "reasoning": (answers.get("_reasoning") or {}).get(item.item_id)
                    if isinstance(answers.get("_reasoning"), dict)
                    else answers.get(f"{item.item_id}__reasoning"),
                }
            )
    return payload


def run_adapt_training(
    responses: list[dict[str, Any]],
    *,
    participant_id: str,
    seed: int = DEFAULT_SEED,
    service: ProductService | None = None,
) -> dict[str, Any]:
    """Drive the real Phase 4 product. Next challenge comes from AdaptiveTutor."""
    product = service or ProductService(seed=seed)
    if not isinstance(product.tutor, AdaptiveTutor):
        raise RuntimeError("ADAPT condition must use AdaptiveTutor")
    remaining = list(responses)
    sessions = []
    steps: list[dict[str, Any]] = []
    strategies: list[str] = []
    correct = 0
    total = 0
    for topic_id in TOPICS:
        needed = TRAINING_STEPS_PER_TOPIC
        view = product.create_session(
            topic_id=topic_id,
            learner_id=f"{participant_id}-{topic_id}",
            session_id=f"{participant_id}-ADAPT-{topic_id}",
            initial_challenge=ADAPT_START[topic_id],
            max_steps=needed,
        )
        topic_steps = []
        for _index in range(needed):
            if not remaining:
                break
            payload = remaining.pop(0)
            result = product.submit_response(
                view["session_id"],
                answer=str(payload.get("answer") or ""),
                confidence=_confidence(payload.get("confidence")),
                reasoning=payload.get("reasoning"),
                challenge_id=view["challenge"]["challenge_id"] if view.get("challenge") else None,
            )
            tutor_session = product.tutor.get_session(view["session_id"])
            last = tutor_session.traces[-1]
            if last.evidence.answer_status.value == "CORRECT":
                correct += 1
            total += 1
            strategies.append(last.decision.value)
            record = {
                "step_number": last.step_number,
                "topic_id": topic_id,
                "challenge_id": last.challenge_id,
                "answer": last.response.answer,
                "confidence": last.response.learner_confidence.value,
                "reasoning": last.response.reasoning,
                "answer_status": last.evidence.answer_status.value,
                "evidence": last.evidence.to_dict(),
                "learner_state": last.state_after.to_dict(),
                "strategy": last.decision.value,
                "reason": last.reason,
                "reason_codes": list(last.reason_codes),
                "next_challenge_id": last.next_challenge_id,
                "timestamp": _now(),
                "trace_id": last.response.response_id,
                "engine": "AdaptiveTutor",
            }
            topic_steps.append(record)
            steps.append(record)
            view = product.get_session(view["session_id"])
        sessions.append(
            {
                "session_id": view["session_id"],
                "topic_id": topic_id,
                "steps": topic_steps,
                "tutor_class": type(product.tutor).__name__,
            }
        )
    return {
        "engine": "AdaptiveTutor",
        "product": "ProductService",
        "sessions": sessions,
        "training": steps,
        "strategies": strategies,
        "training_score": None if total == 0 else correct / total,
        "completed": total == TRAINING_STEPS_PER_TOPIC * len(TOPICS),
        "dropout": total < TRAINING_STEPS_PER_TOPIC * len(TOPICS),
        "session_ids": [item["session_id"] for item in sessions],
    }


def run_baseline_training(
    responses: list[dict[str, Any]],
    *,
    participant_id: str,
    seed: int = DEFAULT_SEED,
) -> dict[str, Any]:
    tutor = LinearTutor(seed=seed)
    steps: list[dict[str, Any]] = []
    correct = 0
    for payload in responses:
        if tutor.complete:
            break
        current = tutor.current_challenge()
        assert current is not None
        conf_raw = payload.get("confidence")
        if isinstance(conf_raw, int):
            confidence = LearnerConfidence.UNKNOWN
        elif isinstance(conf_raw, LearnerConfidence):
            confidence = conf_raw
        elif isinstance(conf_raw, str) and conf_raw in LearnerConfidence._value2member_map_:
            confidence = LearnerConfidence(conf_raw)
        else:
            confidence = LearnerConfidence.UNKNOWN
        step = tutor.submit(
            answer=str(payload.get("answer") or ""),
            confidence=confidence,
            reasoning=payload.get("reasoning"),
            challenge_id=payload.get("challenge_id") or current.challenge_id,
            learner_id=participant_id,
        )
        if step.answer_status == "CORRECT":
            correct += 1
        steps.append(step.to_dict())
    total = len(steps)
    return {
        "engine": "LinearTutor",
        "product": None,
        "sessions": [{"session_id": f"{participant_id}-BASELINE", "steps": steps}],
        "training": steps,
        "strategies": [],
        "training_score": None if total == 0 else correct / total,
        "completed": tutor.complete,
        "dropout": not tutor.complete,
        "session_ids": [f"{participant_id}-BASELINE"],
        "sequence": list(tutor.sequence),
        "uses_adaptive_tutor": False,
    }


def attach_post_and_survey(
    condition_payload: dict[str, Any],
    *,
    condition: str,
    post_answers: dict[str, Any] | None,
    survey: dict[str, Any] | None,
    pre_score: float | None,
) -> dict[str, Any]:
    form = POSTTEST_BY_CONDITION[condition]
    post = score_form(form, post_answers)
    post_reasoning = {}
    if post_answers:
        nested = post_answers.get("_reasoning") if isinstance(post_answers.get("_reasoning"), dict) else {}
        post_reasoning = nested or {
            key.replace("__reasoning", ""): value
            for key, value in post_answers.items()
            if isinstance(key, str) and key.endswith("__reasoning")
        }
    recovery_rows = []
    if post_answers:
        for item in form:
            recovery_rows.append(
                {
                    "item_id": item.item_id,
                    "answer": post_answers.get(item.item_id),
                    "reasoning": post_reasoning.get(item.item_id),
                }
            )
    recovery = evaluate_recovery(
        training_steps=condition_payload.get("training") or [],
        post_items=recovery_rows,
        post_form=form,
    )
    merged = dict(condition_payload)
    merged["post_test"] = post
    merged["post_test_score"] = post["score"]
    merged["gain"] = learning_gain(pre_score, post["score"])
    merged["survey"] = parse_survey(survey)
    merged["misconception_recovery"] = recovery
    return merged


def score_pretest(answers: dict[str, Any] | None) -> dict[str, Any]:
    return score_form(PRETEST, answers)
