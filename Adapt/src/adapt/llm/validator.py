"""Validate Gemini evidence JSON before it can enter AdaptiveTutor."""

from __future__ import annotations

import json
import re
from typing import Any

from adapt.llm.errors import LLMValidationFailure
from adapt.llm.schemas import (
    CONFIDENCE_VALUES,
    CORRECTNESS_VALUES,
    ERROR_TYPE_VALUES,
    FORBIDDEN_DECISION_KEYS,
    FORBIDDEN_STRATEGY_VALUES,
    LLMEvidence,
    REASONING_VALUES,
    REQUIRED_FIELDS,
    STRENGTH_VALUES,
    UNCERTAINTY_VALUES,
)

_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.IGNORECASE | re.DOTALL)


def extract_json_object(text: str) -> dict[str, Any]:
    if text is None:
        raise LLMValidationFailure("empty LLM response")
    stripped = str(text).strip()
    if not stripped:
        raise LLMValidationFailure("empty LLM response")
    fenced = _FENCE_RE.search(stripped)
    candidate = fenced.group(1).strip() if fenced else stripped
    parsed = _loads(candidate)
    if parsed is None:
        start = candidate.find("{")
        end = candidate.rfind("}")
        if start >= 0 and end > start:
            parsed = _loads(candidate[start : end + 1])
    if not isinstance(parsed, dict):
        raise LLMValidationFailure("LLM output is not a JSON object")
    return parsed


def validate_evidence_payload(payload: dict[str, Any]) -> LLMEvidence:
    if not isinstance(payload, dict):
        raise LLMValidationFailure("LLM output is not a JSON object")
    forbidden = sorted(key for key in payload if str(key).lower() in {item.lower() for item in FORBIDDEN_DECISION_KEYS})
    if forbidden:
        raise LLMValidationFailure(
            "LLM output includes adaptive-decision fields: " + ", ".join(forbidden)
        )
    missing = [field for field in REQUIRED_FIELDS if field not in payload]
    if missing:
        raise LLMValidationFailure("LLM output missing required fields: " + ", ".join(missing))
    correctness = _enum(payload.get("correctness"), CORRECTNESS_VALUES, "correctness")
    reasoning = _enum(payload.get("reasoning_quality"), REASONING_VALUES, "reasoning_quality")
    confidence = _enum(payload.get("confidence_signal"), CONFIDENCE_VALUES, "confidence_signal")
    strength = _enum(payload.get("evidence_strength"), STRENGTH_VALUES, "evidence_strength")
    uncertainty = _enum(payload.get("uncertainty"), UNCERTAINTY_VALUES, "uncertainty")
    misconception = _optional_string(payload.get("misconception"), "misconception")
    error_type = _optional_error(payload.get("error_type"))
    supporting = _string_list(payload.get("supporting_evidence"), "supporting_evidence")
    _reject_strategy_tokens(payload)
    return LLMEvidence(
        correctness=correctness,
        reasoning_quality=reasoning,
        confidence_signal=confidence,
        misconception=misconception,
        error_type=error_type,
        evidence_strength=strength,
        uncertainty=uncertainty,
        supporting_evidence=tuple(supporting),
    )


def parse_and_validate(text: str) -> LLMEvidence:
    return validate_evidence_payload(extract_json_object(text))


def _loads(text: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def _enum(value: Any, allowed: tuple[str, ...], field_name: str) -> str:
    if value is None:
        raise LLMValidationFailure(f"{field_name} is required")
    text = str(value).strip().lower()
    if text not in allowed:
        raise LLMValidationFailure(
            f"invalid {field_name}={value!r}. Allowed: {', '.join(allowed)}"
        )
    return text


def _optional_string(value: Any, field_name: str) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    raise LLMValidationFailure(f"{field_name} must be a string or null")


def _optional_error(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str) and value.strip() == "":
        return None
    text = str(value).strip().lower()
    if text in {"none", "null"}:
        return None
    if text not in ERROR_TYPE_VALUES:
        raise LLMValidationFailure(
            f"invalid error_type={value!r}. Allowed: {', '.join(ERROR_TYPE_VALUES)} or null"
        )
    return text


def _string_list(value: Any, field_name: str) -> list[str]:
    if value is None:
        raise LLMValidationFailure(f"{field_name} is required")
    if not isinstance(value, list):
        raise LLMValidationFailure(f"{field_name} must be an array of strings")
    items: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise LLMValidationFailure(f"{field_name} entries must be strings")
        items.append(item)
    return items


def _reject_strategy_tokens(payload: dict[str, Any]) -> None:
    for key, value in payload.items():
        if key == "supporting_evidence":
            continue
        if isinstance(value, str) and value.strip().upper() in FORBIDDEN_STRATEGY_VALUES:
            raise LLMValidationFailure(
                f"LLM output attempts to set adaptive strategy via {key}={value!r}"
            )
