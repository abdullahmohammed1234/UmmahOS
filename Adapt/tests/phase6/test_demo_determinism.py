"""Demo path is deterministic across repeated AdaptiveTutor runs."""

from __future__ import annotations

from adapt.product.demo import load_demo_scenario
from adapt.tutor.tutor import DEFAULT_SEED
from tests.phase4.helpers import make_service


def _run_demo(service):
    scenario = load_demo_scenario()
    view = service.start_demo(scenario=scenario)
    session_id = view["session_id"]
    steps = []
    while True:
        result = service.demo_step(session_id)
        engine = service.tutor.get_trace(session_id)[-1]
        steps.append(
            {
                "decision": result["result"]["adaptation"]["decision"],
                "engine_decision": engine.decision.value,
                "strategy": result["research"]["strategy"]["decision"],
                "challenge_id": result["research"]["next_challenge"]["challenge_id"],
                "trace_reason": result["research"]["strategy"]["reason"],
                "engine_reason": engine.reason,
            }
        )
        if result.get("demo", {}).get("complete") or result.get("complete"):
            break
    return steps


def test_demo_seed_is_frozen():
    service = make_service()
    assert service.seed == DEFAULT_SEED
    assert service.tutor.seed == DEFAULT_SEED


def test_three_demo_runs_are_identical():
    runs = [_run_demo(make_service()) for _ in range(3)]
    assert runs[0] == runs[1] == runs[2]
    assert all(step["decision"] == step["engine_decision"] for step in runs[0])
    assert all(step["trace_reason"] == step["engine_reason"] for step in runs[0])
    decisions = [step["decision"] for step in runs[0]]
    assert "INCREASE" in decisions
    assert "PROBE" in decisions
    assert "REMEDIATE" in decisions


def test_demo_opening_state_is_uncertain():
    view = make_service().start_demo()
    assert view["opening"]["mastery"] == "uncertain"
    assert view["opening"]["confidence"] == "low"
    assert view["opening"]["strategy"] == "ASSESS"
    assert view["demo"]["label"] == "DEMO SCENARIO"
    assert view["current_strategy"] == "ASSESS"
