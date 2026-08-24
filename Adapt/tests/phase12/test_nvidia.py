"""NVIDIA client uses the existing LLMClient boundary. Fallback is not labeled NVIDIA."""

from __future__ import annotations

from adapt.llm.client import LLMGeneration
from adapt.llm.errors import LLMAuthenticationError
from adapt.llm.fallback import SOURCE_FALLBACK, SOURCE_NVIDIA
from adapt.llm.nvidia import NvidiaClient, select_available_model
from adapt.llm.testing import MockLLMClient
from adapt.llm.workflow import EvidenceExtractionWorkflow
from adapt.models.challenge import Challenge
from adapt.models.enums import ChallengeType, Difficulty, LearnerConfidence
from adapt.models.learner_response import LearnerResponse
from tests.phase12.helpers import VALID_EVIDENCE, dumps


def _challenge() -> Challenge:
    return Challenge(
        challenge_id="P12-NV-001",
        concept_id="basic_algebra",
        difficulty=Difficulty.EASY,
        question="Solve 7x = 56",
        challenge_type=ChallengeType.STANDARD,
        expected_answer="8",
    )


def _response() -> LearnerResponse:
    return LearnerResponse(
        response_id="nv1",
        learner_id="l1",
        concept_id="basic_algebra",
        challenge_id="P12-NV-001",
        answer="8",
        reasoning="I guessed.",
        learner_confidence=LearnerConfidence.LOW,
    )


class _NvidiaMock(MockLLMClient):
    provider = "nvidia"


def test_nvidia_without_key_is_unavailable():
    client = NvidiaClient(api_key="", model="meta/llama-3.3-70b-instruct")
    assert client.available() is False
    try:
        client.generate("hello")
    except LLMAuthenticationError as exc:
        assert "NVIDIA_API_KEY" in str(exc)
        assert "nvapi-" not in str(exc)
    else:
        raise AssertionError("expected LLMAuthenticationError")


def test_valid_nvidia_output_is_labeled_nvidia():
    workflow = EvidenceExtractionWorkflow(client=_NvidiaMock(text=dumps(VALID_EVIDENCE)))
    result = workflow.extract(_response(), _challenge())
    assert result.source == SOURCE_NVIDIA
    assert result.validation_ok is True


def test_invalid_nvidia_output_is_fallback_not_nvidia():
    workflow = EvidenceExtractionWorkflow(client=_NvidiaMock(text="not-json"))
    result = workflow.extract(_response(), _challenge())
    assert result.source == SOURCE_FALLBACK
    assert result.source != SOURCE_NVIDIA
    assert result.validation_ok is False


def test_select_available_model_prefers_llama_33():
    chosen = select_available_model(
        ["mistralai/mistral-7b-instruct", "meta/llama-3.3-70b-instruct"],
        preferred="meta/llama-3.3-70b-instruct",
    )
    assert chosen == "meta/llama-3.3-70b-instruct"


def test_nvidia_generation_type_has_provider():
    generation = LLMGeneration(text="{}", model="meta/llama-3.3-70b-instruct", provider="nvidia")
    assert generation.provider == "nvidia"
