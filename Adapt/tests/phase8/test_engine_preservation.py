"""Phase 8 must not change frozen engine decisions."""

from pathlib import Path

from tests.phase4.helpers import make_service, run_kinds_through_product, run_kinds_through_tutor

ENGINE_FILES = (
    "src/adapt/analysis/evidence_analyzer.py",
    "src/adapt/state/state_updater.py",
    "src/adapt/strategy/engine.py",
    "src/adapt/adaptation/adaptation_engine.py",
    "src/adapt/tutor/tutor.py",
)


def test_displayed_decision_equals_adaptive_tutor():
    service = make_service()
    view = service.create_session(
        topic_id="algebra",
        session_id="P8-EN-001",
        initial_challenge="ALG-M-001",
        max_steps=3,
    )
    kinds = ("strong_correct", "weak_correct", "misconception")
    for kind in kinds:
        result = None
        from tests.phase4.helpers import scripted_submit

        result = scripted_submit(service, view["session_id"], kind)
        engine = service.tutor.get_trace(view["session_id"])[-1]
        assert result["result"]["adaptation"]["decision"] == engine.decision.value
        assert result["result"]["explanation"]["decision"] == engine.decision.value
        assert service.engine_decision(view["session_id"]) == engine.decision.value


def test_product_path_matches_direct_tutor():
    kinds = ("strong_correct", "weak_correct")
    _service, _session, product_results = run_kinds_through_product(
        kinds,
        session_id="P8-EN-002",
        learner_id="P8-EN-L",
    )
    _tutor, _tsession, traces = run_kinds_through_tutor(
        kinds,
        session_id="P8-EN-T",
        learner_id="P8-EN-L2",
    )
    product_decisions = [item["result"]["adaptation"]["decision"] for item in product_results]
    tutor_decisions = [item.decision.value for item in traces]
    assert product_decisions == tutor_decisions


def test_engine_modules_do_not_import_phase8_ui():
    root = Path(__file__).resolve().parents[2]
    for relative in ENGINE_FILES:
        text = (root / relative).read_text(encoding="utf-8")
        assert "adapt.product" not in text
        assert "phase8" not in text.lower()


def test_determinism_same_seed():
    a = make_service(seed=20260814)
    b = make_service(seed=20260814)
    cf_a = a.run_counterfactual()
    cf_b = b.run_counterfactual()
    assert cf_a["learner_a"]["final_decision"] == cf_b["learner_a"]["final_decision"]
    assert cf_a["learner_b"]["final_decision"] == cf_b["learner_b"]["final_decision"]
