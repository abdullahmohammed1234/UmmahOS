"""Every strategy decision is auditable."""

from __future__ import annotations

from adapt.models.enums import StrategyName
from adapt.models.strategy import StrategyState
from adapt.strategy.invariants import invariant_8_traceable
from tests.helpers_phase2 import decide, make_evidence, make_state, phase2_pipeline
from tests.helpers import make_response, STRONG_REASONING
from adapt.adaptation.challenge_bank import get_challenge
from adapt.models.enums import LearnerConfidence
from adapt.models.learner_state import initial_learner_state


def test_decision_trace_contract_fields():
    decision = decide(make_state(pattern="CCC"), make_evidence())
    payload = decision.to_dict()
    assert payload["decision"]
    assert payload["reason"]
    assert payload["current_strategy"]
    assert payload["evidence_ids"]
    assert payload["state_snapshot"]
    assert payload["confidence"] is not None
    assert payload["transition"]["label"]
    assert invariant_8_traceable(decision)


def test_pipeline_trace_includes_strategy_chain():
    pipe = phase2_pipeline()
    challenge = get_challenge("ALG-M-001")
    traces = pipe.run_sequence(
        learner_state=initial_learner_state("tr", "basic_algebra"),
        steps=[
            (
                challenge,
                make_response(
                    response_id="T-1",
                    challenge_id=challenge.challenge_id,
                    answer="4",
                    reasoning=STRONG_REASONING,
                    learner_confidence=LearnerConfidence.HIGH,
                    learner_id="tr",
                ),
            )
        ],
    )
    trace = traces[0]
    report = trace.format_report()
    assert trace.strategy_decision is not None
    assert trace.strategy_transition is not None
    assert trace.strategy_state is not None
    assert "Strategy:" in report
    assert "Strategy Transition:" in report
    payload = trace.to_dict()
    assert "evidence" in payload
    assert "learner_state_after" in payload
    assert "strategy_decision" in payload
    assert "strategy_transition" in payload
    assert "adaptation_decision" in payload
    assert "next_challenge" in payload


def test_reason_explains_probe_for_isolated_misconception():
    from adapt.models.enums import AnswerStatus, ErrorPattern, EvidencePolarity, EvidenceStrength
    from adapt.models.learner_state import MisconceptionRecord

    decision = decide(
        make_state(
            pattern="CCCCW",
            mastery=0.7,
            misconceptions=(MisconceptionRecord("DIST_PROP", 1, "SUSPECTED"),),
        ),
        make_evidence(
            answer_status=AnswerStatus.INCORRECT,
            polarity=EvidencePolarity.NEGATIVE,
            misconception_signal="DIST_PROP",
            error_type=ErrorPattern.CONCEPTUAL,
            evidence_strength=EvidenceStrength.MODERATE,
        ),
        strategy=StrategyState(current_strategy=StrategyName.MAINTAIN),
    )
    assert "misconception" in decision.reason.lower()
    assert "PROBE" in decision.transition.label or decision.decision == StrategyName.PROBE


def test_adaptation_decision_still_has_evidence_trail():
    decision = decide(make_state(pattern="CCC"), make_evidence())
    adapt = decision.to_adaptation_decision()
    assert adapt.reason
    assert adapt.evidence_used
    assert adapt.confidence


def test_traceability_survives_serialization():
    decision = decide(make_state(pattern="WWWCCC"), make_evidence(), strategy=StrategyState(current_strategy=StrategyName.REMEDIATE))
    restored_reason = decision.to_dict()["reason"]
    assert restored_reason == decision.reason


def test_why_challenge_was_chosen_is_answerable_from_trace():
    pipe = phase2_pipeline()
    challenge = get_challenge("ALG-D-001")
    from tests.helpers import MISCONCEPTION_REASONING

    traces = pipe.run_sequence(
        learner_state=initial_learner_state("why", "basic_algebra"),
        steps=[
            (
                challenge,
                make_response(
                    response_id=f"W-{i}",
                    challenge_id=challenge.challenge_id,
                    answer="2x+3",
                    reasoning=MISCONCEPTION_REASONING,
                    learner_confidence=LearnerConfidence.HIGH,
                    learner_id="why",
                ),
            )
            for i in range(3)
        ],
    )
    last = traces[-1]
    assert last.strategy_decision.decision == StrategyName.REMEDIATE
    assert last.strategy_decision.evidence_ids
    assert last.next_challenge.challenge_id
    assert last.format_report()
