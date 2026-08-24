"""Fallback is labeled and does not impersonate Gemini."""

from __future__ import annotations

from adapt.llm.errors import LLMTimeoutError, LLMUnavailableError, LLMValidationFailure
from adapt.llm.fallback import SOURCE_FALLBACK, SOURCE_GEMINI, DeterministicFallback
from adapt.llm.testing import MockLLMClient, TimeoutLLMClient
from adapt.llm.workflow import EvidenceExtractionWorkflow
from adapt.models.challenge import Challenge
from adapt.models.enums import ChallengeType, Difficulty, LearnerConfidence
from adapt.models.learner_response import LearnerResponse
from tests.phase12.helpers import VALID_EVIDENCE, dumps


def _challenge() -> Challenge:
    return Challenge(
        challenge_id="P12-T-001",
        concept_id="basic_algebra",
        difficulty=Difficulty.EASY,
        question="Solve 7x = 56",
        challenge_type=ChallengeType.STANDARD,
        expected_answer="8",
        expected_reasoning_cues=("divide", "both sides"),
        correct_method_cues=("divide",),
    )


def _response(*, answer="8", reasoning="I guessed.", confidence=LearnerConfidence.LOW) -> LearnerResponse:
    return LearnerResponse(
        response_id="r1",
        learner_id="l1",
        concept_id="basic_algebra",
        challenge_id="P12-T-001",
        answer=answer,
        reasoning=reasoning,
        learner_confidence=confidence,
    )


def test_valid_gemini_output_is_labeled_gemini():
    workflow = EvidenceExtractionWorkflow(client=MockLLMClient(text=dumps(VALID_EVIDENCE)))
    result = workflow.extract(_response(), _challenge())
    assert result.source == SOURCE_GEMINI
    assert result.validation_ok is True
    assert result.evidence.answer_status.value == "CORRECT"


def test_invalid_json_uses_fallback_not_gemini():
    workflow = EvidenceExtractionWorkflow(client=MockLLMClient(text="nope"))
    result = workflow.extract(_response(), _challenge())
    assert result.source == SOURCE_FALLBACK
    assert result.failure_code == "LLM_VALIDATION_FAILURE"
    assert result.validation_ok is False


def test_timeout_uses_fallback():
    workflow = EvidenceExtractionWorkflow(client=TimeoutLLMClient())
    result = workflow.extract(_response(), _challenge())
    assert result.source == SOURCE_FALLBACK
    assert result.failure_code == "LLM_TIMEOUT"


def test_unavailable_without_client_uses_fallback():
    from adapt.llm.testing import UnavailableLLMClient

    workflow = EvidenceExtractionWorkflow(client=UnavailableLLMClient())
    result = workflow.extract(_response(), _challenge())
    assert result.source == SOURCE_FALLBACK
    assert result.failure_code == "LLM_UNAVAILABLE"


def test_fallback_matches_deterministic_analyzer():
    fallback = DeterministicFallback()
    challenge = _challenge()
    response = _response()
    direct = fallback.analyze(response, challenge)
    workflow = EvidenceExtractionWorkflow(client=MockLLMClient(text="{{{"))
    result = workflow.extract(response, challenge)
    assert result.evidence == direct


def test_validation_failure_code_is_stable():
    assert LLMValidationFailure.code == "LLM_VALIDATION_FAILURE"
    assert LLMUnavailableError.code == "LLM_UNAVAILABLE"
