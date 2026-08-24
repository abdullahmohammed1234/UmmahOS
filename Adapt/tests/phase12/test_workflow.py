"""Workflow nodes and single-prompt baseline."""

from __future__ import annotations

from adapt.llm.baseline import SinglePromptBaseline
from adapt.llm.testing import MockLLMClient
from adapt.llm.workflow import (
    NODE_GEMINI_EXTRACTION,
    NODE_HUMAN_INPUT,
    NODE_VALIDATION,
    EvidenceExtractionWorkflow,
    attach_adapt_nodes,
)
from adapt.models.challenge import Challenge
from adapt.models.enums import ChallengeType, Difficulty, LearnerConfidence
from adapt.models.learner_response import LearnerResponse
from tests.phase12.helpers import VALID_EVIDENCE, dumps


def _challenge() -> Challenge:
    return Challenge(
        challenge_id="P12-W",
        concept_id="basic_algebra",
        difficulty=Difficulty.EASY,
        question="7x=56",
        challenge_type=ChallengeType.STANDARD,
        expected_answer="8",
    )


def _response() -> LearnerResponse:
    return LearnerResponse(
        response_id="w1",
        learner_id="l",
        concept_id="basic_algebra",
        challenge_id="P12-W",
        answer="8",
        reasoning="I guessed.",
        learner_confidence=LearnerConfidence.LOW,
        metadata={"approach": "I guessed", "explanation": "I guessed."},
    )


def test_workflow_records_human_gemini_validation_nodes():
    workflow = EvidenceExtractionWorkflow(client=MockLLMClient(text=dumps(VALID_EVIDENCE)))
    result = workflow.extract(_response(), _challenge())
    names = [node.name for node in result.nodes]
    assert NODE_HUMAN_INPUT in names
    assert NODE_GEMINI_EXTRACTION in names
    assert NODE_VALIDATION in names
    result = attach_adapt_nodes(
        result,
        state={"mastery": 0.4},
        strategy={"decision": "PROBE"},
        challenge={"challenge_id": "NEXT"},
        feedback={"noticed": "Low confidence"},
    )
    assert [node.id for node in result.nodes] == ["1", "2", "3", "4", "5", "6", "7"]


def test_baseline_parses_single_prompt_action():
    client = MockLLMClient(
        text=dumps(
            {
                "next_action": "INCREASE",
                "mastery": "high",
                "message": "Go harder",
                "reason": "correct",
            }
        )
    )
    baseline = SinglePromptBaseline(client=client)
    result = baseline.run(_response(), _challenge())
    assert result.valid is True
    assert result.next_action == "INCREASE"
    assert result.to_dict()["architecture"] == "single_prompt"


def test_baseline_invalid_action():
    client = MockLLMClient(text=dumps({"next_action": "DANCE", "message": "x"}))
    result = SinglePromptBaseline(client=client).run(_response(), _challenge())
    assert result.valid is False
    assert result.failure_code == "LLM_VALIDATION_FAILURE"


def test_prompt_versions_exist():
    from adapt.llm.prompts import EVIDENCE_PROMPT_IDS, load_prompt

    for prompt_id in EVIDENCE_PROMPT_IDS:
        text = load_prompt(prompt_id)
        assert "{{LEARNER_BLOCK}}" in text or "LEARNER" in text or "evidence" in text.lower()
    assert "INCREASE" in load_prompt("evidence_v3")
    assert "untrusted" in load_prompt("evidence_v3").lower()
    assert "untrusted" not in load_prompt("evidence_v1").lower()
