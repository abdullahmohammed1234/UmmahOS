"""End-to-end trace completeness and explainability tests."""

from __future__ import annotations

from tests.helpers_phase3 import run_kinds


REQUIRED = (
    "challenge_id",
    "response",
    "evidence",
    "state_before",
    "state_after",
    "strategy_before",
    "strategy_after",
    "decision",
    "next_challenge_id",
)


def test_every_step_has_complete_trace_fields():
    _, _, traces = run_kinds(("strong_correct", "weak_correct", "misconception"), session_id="TR-1", initial_challenge="ALG-M-002")
    for item in traces:
        assert item.is_complete()
        payload = item.to_dict()
        for field in REQUIRED:
            assert payload.get(field) not in (None, "", [])


def test_trace_connects_response_to_next_challenge():
    _, _, traces = run_kinds(("strong_correct",), session_id="TR-2")
    item = traces[0]
    assert item.challenge_id == item.response.challenge_id
    assert item.evidence.response_id == item.response.response_id
    assert item.next_challenge.challenge_id == item.next_challenge_id


def test_state_before_after_are_auditable():
    _, _, traces = run_kinds(("strong_correct", "strong_correct"), session_id="TR-3")
    assert traces[1].state_before == traces[0].state_after
    assert traces[0].state_before.mastery_estimate == 0.5


def test_strategy_before_after_are_auditable():
    _, _, traces = run_kinds(("strong_correct", "strong_correct"), session_id="TR-4")
    assert traces[1].strategy_before == traces[0].strategy_after
    assert traces[0].strategy_before.current_strategy.value == "ASSESS"


def test_explanation_answers_required_questions():
    tutor, session, traces = run_kinds(("misconception",), session_id="TR-5", initial_challenge="ALG-M-002")
    text = tutor.explain("TR-5")
    assert "Strategy:" in text
    assert "Reason:" in text
    assert "Evidence:" in text
    assert "State:" in text
    assert "Next challenge:" in text
    assert traces[0].explanation
    assert session.traces[0].explanation == traces[0].explanation


def test_explanation_includes_why_strategy_and_difficulty():
    tutor, _, _ = run_kinds(("strong_correct",) * 3, session_id="TR-6")
    text = tutor.explain("TR-6")
    assert "Why this strategy was selected" in text
    assert "Difficulty:" in text


def test_trace_round_trip_dict():
    _, _, traces = run_kinds(("moderate_correct",), session_id="TR-7")
    payload = traces[0].to_dict()
    from adapt.tutor.session import StepTrace

    restored = StepTrace.from_dict(payload)
    assert restored.challenge_id == traces[0].challenge_id
    assert restored.decision == traces[0].decision
    assert restored.next_challenge_id == traces[0].next_challenge_id


def test_pipeline_trace_is_present():
    _, _, traces = run_kinds(("strong_correct",), session_id="TR-8")
    assert traces[0].pipeline_trace.evidence.response_id == traces[0].evidence.response_id
    assert traces[0].pipeline_trace.next_challenge.challenge_id == traces[0].next_challenge_id
