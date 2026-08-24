"""M9-007 — Product does not override AdaptiveTutor decisions."""

from pathlib import Path

from tests.phase4.helpers import make_service, run_kinds_through_product, run_kinds_through_tutor, scripted_submit

ENGINE_FILES = (
    "src/adapt/analysis/evidence_analyzer.py",
    "src/adapt/state/state_updater.py",
    "src/adapt/strategy/engine.py",
    "src/adapt/adaptation/adaptation_engine.py",
    "src/adapt/tutor/tutor.py",
)


def test_m9_007_strategy_preservation():
    service = make_service()
    view = service.create_session(
        topic_id="algebra",
        session_id="P9-ST-001",
        initial_challenge="ALG-M-001",
        max_steps=3,
    )
    for kind in ("strong_correct", "weak_correct"):
        result = scripted_submit(service, view["session_id"], kind)
        engine = service.tutor.get_trace(view["session_id"])[-1]
        assert result["result"]["adaptation"]["decision"] == engine.decision.value
        assert result["result"]["adaptation_view"]["decision"] == engine.decision.value
        assert service.engine_decision(view["session_id"]) == engine.decision.value


def test_m9_007_product_matches_direct_tutor():
    kinds = ("strong_correct", "weak_correct")
    _service, _session, product_results = run_kinds_through_product(
        kinds,
        session_id="P9-ST-002",
        learner_id="P9-ST-L",
    )
    _tutor, _tsession, traces = run_kinds_through_tutor(
        kinds,
        session_id="P9-ST-T",
        learner_id="P9-ST-L2",
    )
    product_decisions = [item["result"]["adaptation"]["decision"] for item in product_results]
    tutor_decisions = [item.decision.value for item in traces]
    assert product_decisions == tutor_decisions


def test_m9_007_engine_does_not_import_phase9():
    root = Path(__file__).resolve().parents[2]
    for relative in ENGINE_FILES:
        text = (root / relative).read_text(encoding="utf-8")
        assert "adapt.product" not in text
        assert "phase9" not in text.lower()
        assert "increaseDifficulty" not in text
