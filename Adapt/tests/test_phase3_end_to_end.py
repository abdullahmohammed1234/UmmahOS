"""End-to-end adaptive loop tests."""

from __future__ import annotations

from adapt.models.enums import StrategyName
from tests.helpers_phase3 import run_kinds


def test_full_loop_updates_state_strategy_and_challenge():
    tutor, session, traces = run_kinds(
        ("strong_correct", "strong_correct", "strong_correct", "strong_correct"),
        session_id="E2E-1",
    )
    first = traces[0]
    assert first.evidence.response_id
    assert first.state_after.mastery_estimate != first.state_before.mastery_estimate or first.state_after.uncertainty != first.state_before.uncertainty
    assert session.current_challenge.challenge_id == traces[-1].next_challenge_id
    assert session.step_number == 4


def test_response_flows_through_evidence_analysis():
    _, _, traces = run_kinds(("strong_correct",), session_id="E2E-EV")
    evidence = traces[0].evidence
    assert evidence.answer_status.value == "CORRECT"
    assert evidence.reasoning_quality.value == "STRONG"


def test_evidence_updates_learner_state():
    _, session, traces = run_kinds(("strong_correct",), session_id="E2E-ST")
    assert session.learner_state == traces[0].state_after
    assert traces[0].state_after.mastery_estimate >= traces[0].state_before.mastery_estimate


def test_state_influences_strategy_over_steps():
    _, session, traces = run_kinds(
        ("strong_correct",) * 5,
        session_id="E2E-STRAT",
    )
    names = [item.decision.value for item in traces]
    assert names[0] in {"ASSESS", "GATHER_EVIDENCE", "PROBE", "MAINTAIN"}
    assert "INCREASE" in names or session.strategy_state.current_strategy in {
        StrategyName.INCREASE,
        StrategyName.MAINTAIN,
        StrategyName.GATHER_EVIDENCE,
    }


def test_strategy_influences_next_challenge():
    _, _, traces = run_kinds(("strong_correct",) * 5, session_id="E2E-CH")
    last = traces[-1]
    assert last.next_challenge_id
    assert last.next_challenge.challenge_id == last.next_challenge_id
    if last.decision == StrategyName.INCREASE:
        assert last.next_challenge.difficulty.value in {"MEDIUM", "HARD"}


def test_weak_evidence_does_not_increase_as_fast_as_strong():
    _, strong, _ = run_kinds(("strong_correct",) * 4, session_id="E2E-S", learner_id="LS")
    _, weak, _ = run_kinds(("weak_correct",) * 4, session_id="E2E-W", learner_id="LW")
    assert strong.learner_state.mastery_estimate > weak.learner_state.mastery_estimate
    assert weak.strategy_state.current_strategy != StrategyName.INCREASE


def test_each_step_is_causal_chain():
    _, _, traces = run_kinds(("strong_correct", "misconception"), session_id="E2E-CAUS", initial_challenge="ALG-M-002")
    for item in traces:
        assert item.challenge_id
        assert item.response.answer is not None
        assert item.evidence.response_id
        assert item.state_before.learner_id
        assert item.state_after.learner_id
        assert item.strategy_before.current_strategy
        assert item.strategy_after.current_strategy
        assert item.decision
        assert item.next_challenge_id


def test_tutor_gathers_before_aggressive_difficulty():
    _, _, traces = run_kinds(("strong_correct",), session_id="E2E-GATH")
    assert traces[0].decision in {
        StrategyName.ASSESS,
        StrategyName.GATHER_EVIDENCE,
        StrategyName.PROBE,
        StrategyName.MAINTAIN,
    }


def test_multiple_steps_accumulate_history():
    _, session, traces = run_kinds(("moderate_correct",) * 3, session_id="E2E-HIST")
    assert len(session.history) == 3
    assert len(session.recent_evidence) == 3
    assert session.history[0].response_id != session.history[1].response_id


def test_same_inputs_same_seed_reproduce_trajectory():
    _, a, _ = run_kinds(("strong_correct",) * 4, session_id="DET-A", learner_id="D1")
    _, b, _ = run_kinds(("strong_correct",) * 4, session_id="DET-B", learner_id="D1")
    assert [t.decision for t in a.traces] == [t.decision for t in b.traces]
    assert [t.next_challenge_id for t in a.traces] == [t.next_challenge_id for t in b.traces]


def test_wrong_answers_do_not_increase():
    _, session, traces = run_kinds(("wrong_weak",) * 4, session_id="E2E-W4")
    assert all(item.decision != StrategyName.INCREASE for item in traces)
    assert session.strategy_state.current_strategy != StrategyName.INCREASE
