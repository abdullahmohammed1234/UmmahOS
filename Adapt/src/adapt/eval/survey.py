"""Learner perception survey. Items frozen before analysis."""

from __future__ import annotations

from typing import Any

SURVEY_ITEMS = (
    {
        "id": "Q1",
        "metric": "perceived_adaptiveness",
        "prompt": "The tutor seemed to adapt to my responses.",
    },
    {
        "id": "Q2",
        "metric": "challenge_appropriateness",
        "prompt": "The difficulty of the questions felt appropriate for my understanding.",
    },
    {
        "id": "Q3",
        "metric": "explanation_clarity",
        "prompt": "I understood why the next challenge was given to me.",
    },
    {
        "id": "Q4",
        "metric": "learning_helpfulness",
        "prompt": "The tutoring experience helped me understand the material.",
    },
    {
        "id": "Q5",
        "metric": "would_use_again",
        "prompt": "I would use this tutor again.",
    },
)

OPEN_ITEMS = (
    {
        "id": "Q6",
        "key": "what_changed",
        "prompt": "What did the tutor seem to change based on your answers?",
    },
    {
        "id": "Q7",
        "key": "confusing",
        "prompt": "Was anything confusing?",
    },
)

LIKERT_MIN = 1
LIKERT_MAX = 5
LIKERT_LABELS = {
    1: "Strongly disagree",
    2: "Disagree",
    3: "Neutral",
    4: "Agree",
    5: "Strongly agree",
}


def empty_survey() -> dict[str, Any]:
    payload: dict[str, Any] = {item["metric"]: None for item in SURVEY_ITEMS}
    payload["what_changed"] = None
    payload["confusing"] = None
    payload["collected"] = False
    return payload


def parse_survey(raw: dict[str, Any] | None) -> dict[str, Any]:
    if not raw:
        return empty_survey()
    payload = empty_survey()
    collected = False
    for item in SURVEY_ITEMS:
        value = raw.get(item["metric"], raw.get(item["id"]))
        if value is None:
            continue
        number = int(value)
        if number < LIKERT_MIN or number > LIKERT_MAX:
            raise ValueError(f"{item['id']} must be an integer from 1 to 5")
        payload[item["metric"]] = number
        collected = True
    for item in OPEN_ITEMS:
        text = raw.get(item["key"], raw.get(item["id"]))
        if text is None:
            continue
        payload[item["key"]] = str(text)
        collected = True
    payload["collected"] = collected
    return payload
