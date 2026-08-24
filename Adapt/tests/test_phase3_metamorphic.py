"""Phase 3 metamorphic tests."""

from __future__ import annotations

from dataclasses import replace

from adapt.tutor.responses import IRRELEVANT_TEXT, build_scripted_response
from tests.helpers_phase3 import make_tutor, run_kinds


def test_m3_meta_001_irrelevant_text_does_not_change_decision():
    tutor_a = make_tutor()
    tutor_b = make_tutor()
    tutor_a.start_session(learner_id="A", session_id="M1A", initial_challenge="ALG-M-001")
    tutor_b.start_session(learner_id="B", session_id="M1B", initial_challenge="ALG-M-001")
    ch_a = tutor_a.get_next_challenge("M1A")
    ch_b = tutor_b.get_next_challenge("M1B")
    base = build_scripted_response(ch_a, "strong_correct", learner_id="A", response_id="R1")
    extra = build_scripted_response(
        ch_b, "strong_correct", learner_id="B", response_id="R1", extra_text=IRRELEVANT_TEXT
    )
    a = tutor_a.submit_response("M1A", base)
    b = tutor_b.submit_response("M1B", extra)
    assert a.decision == b.decision
    assert a.next_challenge_id == b.next_challenge_id


def test_m3_meta_002_reordering_metadata_does_not_change_decision():
    tutor_a = make_tutor()
    tutor_b = make_tutor()
    tutor_a.start_session(learner_id="A", session_id="M2A", initial_challenge="ALG-M-001")
    tutor_b.start_session(learner_id="B", session_id="M2B", initial_challenge="ALG-M-001")
    ch_a = tutor_a.get_next_challenge("M2A")
    ch_b = tutor_b.get_next_challenge("M2B")
    a = tutor_a.submit_response(
        "M2A",
        build_scripted_response(ch_a, "strong_correct", learner_id="A", response_id="R1", metadata={"z": 1, "a": 2}),
    )
    b = tutor_b.submit_response(
        "M2B",
        build_scripted_response(ch_b, "strong_correct", learner_id="B", response_id="R1", metadata={"a": 2, "z": 1}),
    )
    assert a.decision == b.decision
    assert a.evidence.answer_status == b.evidence.answer_status


def test_m3_meta_003_equivalent_responses_produce_equivalent_evidence():
    tutor = make_tutor()
    tutor.start_session(learner_id="A", session_id="M3", initial_challenge="ALG-M-001")
    ch = tutor.get_next_challenge("M3")
    r1 = build_scripted_response(ch, "strong_correct", learner_id="A", response_id="E1")
    r2 = replace(r1, response_id="E2", answer=f"x = {ch.expected_answer}")
    r3 = replace(r1, response_id="E3", answer=f"answer is {ch.expected_answer}")
    ev1 = tutor.pipeline.analyzer.analyze(r1, ch)
    ev2 = tutor.pipeline.analyzer.analyze(r2, ch)
    ev3 = tutor.pipeline.analyzer.analyze(r3, ch)
    assert ev1.answer_status == ev2.answer_status == ev3.answer_status
    assert ev1.reasoning_quality == ev2.reasoning_quality


def test_m3_meta_004_duplicated_irrelevant_signal_is_not_mastery():
    _, session, traces = run_kinds(
        ("weak_correct",),
        session_id="M4",
    )
    tutor = make_tutor()
    tutor.start_session(learner_id="D", session_id="M4B", initial_challenge="ALG-M-001")
    ch = tutor.get_next_challenge("M4B")
    response = build_scripted_response(
        ch, "weak_correct", learner_id="D", response_id="R1", extra_text=(" hello" * 40)
    )
    step = tutor.submit_response("M4B", response)
    assert step.decision.value != "INCREASE"
    assert step.state_after.mastery_estimate < 0.7
    assert traces[0].decision.value != "INCREASE"


def test_m3_meta_005_harder_instruction_does_not_override():
    tutor = make_tutor()
    tutor.start_session(learner_id="H", session_id="M5", initial_challenge="ALG-M-001")
    ch = tutor.get_next_challenge("M5")
    response = build_scripted_response(ch, "adversarial_harder", learner_id="H", response_id="R1")
    step = tutor.submit_response("M5", response)
    assert step.decision.value != "INCREASE"
    assert step.decision.value in {"ASSESS", "GATHER_EVIDENCE", "PROBE", "MAINTAIN"}
