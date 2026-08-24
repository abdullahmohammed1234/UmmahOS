"""Phase 5 must not rewrite historical artifacts or Phase 3/4 engine decisions."""

from __future__ import annotations

import hashlib
from pathlib import Path

from adapt.eval.experiment import run_adapt_training
from adapt.product.service import ProductService
from adapt.tutor.responses import build_scripted_response
from benchmarks.phase5.expected import HISTORICAL_ARTIFACTS, HISTORICAL_SHA256
from tests.phase4.helpers import run_kinds_through_product, run_kinds_through_tutor

ROOT = Path(__file__).resolve().parents[2]


def test_historical_phase_artifacts_exist():
    for relative in HISTORICAL_ARTIFACTS:
        assert (ROOT / relative).exists(), relative


def test_historical_phase_artifacts_were_not_rewritten():
    for relative, expected in HISTORICAL_SHA256.items():
        digest = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        assert digest == expected, relative


def test_product_still_preserves_phase3_decisions():
    kinds = ("strong_correct", "weak_correct", "strong_correct")
    _, _, product_results = run_kinds_through_product(kinds, session_id="P5-REG-P")
    _, _, tutor_traces = run_kinds_through_tutor(kinds, session_id="P5-REG-T")
    assert [item["result"]["adaptation"]["decision"] for item in product_results] == [
        item.decision.value for item in tutor_traces
    ]


def test_phase5_adapt_wrapper_does_not_replace_tutor():
    service = ProductService(seed=20260814)
    view = service.create_session(
        topic_id="algebra",
        learner_id="reg",
        session_id="P5-REG-SRC",
        max_steps=1,
        initial_challenge="ALG-D-001",
    )
    challenge = service.tutor.get_session(view["session_id"]).current_challenge
    scripted = build_scripted_response(
        challenge, "strong_correct", learner_id="reg", response_id="reg-1"
    )
    responses = [
        {"answer": scripted.answer, "confidence": 5, "reasoning": scripted.reasoning}
    ] * 8
    payload = run_adapt_training(
        responses, participant_id="P5-REG-ADAPT", service=ProductService(seed=20260814)
    )
    assert payload["engine"] == "AdaptiveTutor"
    assert all(step["engine"] == "AdaptiveTutor" for step in payload["training"])
