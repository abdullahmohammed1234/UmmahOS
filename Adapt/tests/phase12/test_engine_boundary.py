"""Gemini cannot modify learner state or choose the next challenge."""

from __future__ import annotations

from adapt.analysis.evidence_analyzer import EvidenceAnalyzer
from adapt.llm.analyzer import LLMEvidenceAnalyzer
from adapt.llm.testing import MockLLMClient
from adapt.state.state_updater import StateUpdater
from adapt.strategy.engine import AdaptiveStrategyEngine
from adapt.tutor.tutor import AdaptiveTutor
from tests.phase12.helpers import STRONG_EVIDENCE, VALID_EVIDENCE, dumps


CHALLENGE_ID = "ALG-M-001"


def test_gemini_cannot_set_strategy_field():
    payload = dict(VALID_EVIDENCE)
    payload["strategy"] = "INCREASE"
    analyzer = LLMEvidenceAnalyzer(client=MockLLMClient(text=dumps(payload)))
    tutor = AdaptiveTutor(analyzer=analyzer, seed=20260819)
    tutor.start_session(learner_id="b1", session_id="P12-B-1", initial_challenge=CHALLENGE_ID)
    step = tutor.submit_response(
        "P12-B-1",
        {"answer": "x=2", "learner_confidence": "LOW", "reasoning": "I guessed."},
    )
    assert analyzer.last_result.failure_code == "LLM_VALIDATION_FAILURE"
    assert step.decision.value != "INCREASE" or analyzer.last_result.source == "DETERMINISTIC_FALLBACK"


def test_gemini_cannot_choose_next_challenge():
    payload = dict(VALID_EVIDENCE)
    payload["next_challenge"] = "HARD-999"
    analyzer = LLMEvidenceAnalyzer(client=MockLLMClient(text=dumps(payload)))
    tutor = AdaptiveTutor(analyzer=analyzer, seed=20260819)
    tutor.start_session(learner_id="b2", session_id="P12-B-2", initial_challenge=CHALLENGE_ID)
    step = tutor.submit_response(
        "P12-B-2",
        {"answer": "x=2", "learner_confidence": "LOW", "reasoning": "I guessed."},
    )
    assert step.next_challenge.challenge_id != "HARD-999"
    assert analyzer.last_result.source == "DETERMINISTIC_FALLBACK"


def test_state_update_still_uses_state_updater():
    analyzer = LLMEvidenceAnalyzer(client=MockLLMClient(text=dumps(STRONG_EVIDENCE)))
    tutor = AdaptiveTutor(analyzer=analyzer, seed=20260819)
    assert isinstance(tutor.pipeline.updater, StateUpdater)
    assert isinstance(tutor.pipeline.strategy_engine, AdaptiveStrategyEngine)
    tutor.start_session(learner_id="b3", session_id="P12-B-3", initial_challenge=CHALLENGE_ID)
    before = tutor.get_state("P12-B-3")
    step = tutor.submit_response(
        "P12-B-3",
        {
            "answer": "2",
            "learner_confidence": "HIGH",
            "reasoning": "I used inverse operations and divided both sides.",
        },
    )
    assert step.state_after is not before
    assert analyzer.last_result.source == "GEMINI"
    assert step.evidence.response_id == step.response.response_id


def test_weak_gemini_evidence_does_not_force_increase():
    analyzer = LLMEvidenceAnalyzer(client=MockLLMClient(text=dumps(VALID_EVIDENCE)))
    tutor = AdaptiveTutor(analyzer=analyzer, seed=20260819)
    tutor.start_session(learner_id="b4", session_id="P12-B-4", initial_challenge=CHALLENGE_ID)
    step = tutor.submit_response(
        "P12-B-4",
        {"answer": "2", "learner_confidence": "LOW", "reasoning": "I guessed."},
    )
    assert step.decision.value != "INCREASE"


def test_default_tutor_still_uses_deterministic_analyzer():
    tutor = AdaptiveTutor(seed=20260819)
    assert type(tutor.pipeline.analyzer) is EvidenceAnalyzer
