"""Map the learner-facing 1–5 confidence scale onto engine LearnerConfidence."""

from __future__ import annotations

from adapt.models.enums import LearnerConfidence
from adapt.product.errors import InvalidResponseError

CONFIDENCE_SCALE = (
    {"value": 1, "label": "Not confident", "engine": LearnerConfidence.LOW},
    {"value": 2, "label": "Slightly confident", "engine": LearnerConfidence.LOW},
    {"value": 3, "label": "Somewhat confident", "engine": LearnerConfidence.MODERATE},
    {"value": 4, "label": "Confident", "engine": LearnerConfidence.HIGH},
    {"value": 5, "label": "Very confident", "engine": LearnerConfidence.HIGH},
)

_BY_VALUE = {int(item["value"]): item for item in CONFIDENCE_SCALE}


def scale_options() -> list[dict[str, int | str]]:
    return [{"value": item["value"], "label": item["label"]} for item in CONFIDENCE_SCALE]


def to_engine_confidence(value: int | str | LearnerConfidence | None) -> LearnerConfidence:
    if isinstance(value, LearnerConfidence):
        return value
    if value is None:
        raise InvalidResponseError("confidence is required")
    if isinstance(value, str) and value in LearnerConfidence._value2member_map_:
        return LearnerConfidence(value)
    try:
        numeric = int(value)
    except (TypeError, ValueError) as exc:
        raise InvalidResponseError("confidence must be a number from 1 to 5") from exc
    item = _BY_VALUE.get(numeric)
    if item is None:
        raise InvalidResponseError("confidence must be a number from 1 to 5")
    return item["engine"]  # type: ignore[return-value]


def label_for(value: int) -> str:
    item = _BY_VALUE.get(int(value))
    if item is None:
        raise InvalidResponseError("confidence must be a number from 1 to 5")
    return str(item["label"])
