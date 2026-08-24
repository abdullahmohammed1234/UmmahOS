"""Deterministic replay and missing-data handling."""

from __future__ import annotations

import json
from pathlib import Path

from adapt.eval.experiment import run_adapt_training, run_baseline_training
from adapt.eval.records import new_record, save_raw_record
from adapt.eval.scoring import paired_delta
from adapt.eval.synthetic import SYNTHETIC_CASES, synthetic_records
from adapt.product.service import ProductService
from adapt.tutor.responses import build_scripted_response


def test_synthetic_deltas_replay():
    for spec in SYNTHETIC_CASES:
        record = spec["record"]
        observed = paired_delta(record["adapt"]["gain"], record["baseline"]["gain"])
        assert observed == spec["expected_delta"]


def test_raw_record_refuses_overwrite(tmp_path: Path):
    record = new_record("P001", condition_order=["ADAPT", "BASELINE"])
    save_raw_record(record, raw_dir=tmp_path)
    try:
        save_raw_record(record, raw_dir=tmp_path)
        raise AssertionError("overwrite should have been refused")
    except FileExistsError:
        original = json.loads((tmp_path / "P001.json").read_text(encoding="utf-8"))
        assert original["participant_id"] == "P001"


def test_adapt_and_baseline_replay_same_inputs():
    service = ProductService(seed=20260814)
    view = service.create_session(
        topic_id="algebra",
        learner_id="rep",
        session_id="P5-REP-SRC",
        max_steps=1,
        initial_challenge="ALG-D-001",
    )
    challenge = service.tutor.get_session(view["session_id"]).current_challenge
    scripted = build_scripted_response(
        challenge, "moderate_correct", learner_id="rep", response_id="rep-1"
    )
    responses = [
        {"answer": scripted.answer, "confidence": 3, "reasoning": scripted.reasoning}
    ] * 8
    first = run_adapt_training(
        responses, participant_id="P5-REP-A", service=ProductService(seed=20260814)
    )
    second = run_adapt_training(
        list(responses), participant_id="P5-REP-B", service=ProductService(seed=20260814)
    )
    assert [step["strategy"] for step in first["training"]] == [
        step["strategy"] for step in second["training"]
    ]
    assert [step["next_challenge_id"] for step in first["training"]] == [
        step["next_challenge_id"] for step in second["training"]
    ]
    base_a = run_baseline_training(responses, participant_id="P5-REP-BL-A")
    base_b = run_baseline_training(responses, participant_id="P5-REP-BL-B")
    assert [step["challenge_id"] for step in base_a["training"]] == [
        step["challenge_id"] for step in base_b["training"]
    ]


def test_missing_human_records_stay_missing():
    assert all(item["source"] == "synthetic" for item in synthetic_records())
