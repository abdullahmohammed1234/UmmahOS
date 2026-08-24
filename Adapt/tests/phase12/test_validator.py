"""Schema validation rejects malformed Gemini output."""

from __future__ import annotations

import pytest

from adapt.llm.errors import LLMValidationFailure
from adapt.llm.validator import extract_json_object, parse_and_validate
from tests.phase12.helpers import VALID_EVIDENCE, dumps


def test_valid_json_passes():
    evidence = parse_and_validate(dumps(VALID_EVIDENCE))
    assert evidence.correctness == "correct"
    assert evidence.reasoning_quality == "weak"


def test_fenced_json_is_extracted():
    text = "```json\n" + dumps(VALID_EVIDENCE) + "\n```"
    evidence = parse_and_validate(text)
    assert evidence.evidence_strength == "weak"


def test_empty_response_fails():
    with pytest.raises(LLMValidationFailure) as exc:
        parse_and_validate("   ")
    assert exc.value.code == "LLM_VALIDATION_FAILURE"


def test_invalid_json_fails():
    with pytest.raises(LLMValidationFailure):
        extract_json_object("not json at all")


def test_missing_fields_fail():
    payload = dict(VALID_EVIDENCE)
    del payload["uncertainty"]
    with pytest.raises(LLMValidationFailure) as exc:
        parse_and_validate(dumps(payload))
    assert "uncertainty" in str(exc.value)


def test_invalid_enum_fails():
    payload = dict(VALID_EVIDENCE)
    payload["correctness"] = "mastered"
    with pytest.raises(LLMValidationFailure):
        parse_and_validate(dumps(payload))


def test_strategy_field_is_rejected():
    payload = dict(VALID_EVIDENCE)
    payload["strategy"] = "INCREASE"
    with pytest.raises(LLMValidationFailure) as exc:
        parse_and_validate(dumps(payload))
    assert "adaptive-decision" in str(exc.value) or "strategy" in str(exc.value).lower()


def test_strategy_value_in_decision_field_rejected():
    payload = dict(VALID_EVIDENCE)
    payload["next_action"] = "PROBE"
    with pytest.raises(LLMValidationFailure):
        parse_and_validate(dumps(payload))


def test_supporting_evidence_must_be_string_list():
    payload = dict(VALID_EVIDENCE)
    payload["supporting_evidence"] = [1, 2]
    with pytest.raises(LLMValidationFailure):
        parse_and_validate(dumps(payload))


def test_malformed_object_rejected():
    with pytest.raises(LLMValidationFailure):
        parse_and_validate("[1, 2, 3]")
