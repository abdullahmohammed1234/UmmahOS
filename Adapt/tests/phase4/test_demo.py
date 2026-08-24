"""Deterministic guided demo through the product boundary."""

from __future__ import annotations

from adapt.product.demo import load_demo_scenario
from tests.phase4.helpers import make_service


def test_demo_is_deterministic_and_uses_engine():
    scenario = load_demo_scenario()
    service_a = make_service()
    service_b = make_service()
    a = service_a.start_demo(scenario=scenario)
    b = service_b.start_demo(scenario=scenario)
    decisions_a = []
    decisions_b = []
    challenges_a = []
    challenges_b = []
    while True:
        ra = service_a.demo_step(a["session_id"])
        rb = service_b.demo_step(b["session_id"])
        decisions_a.append(ra["result"]["adaptation"]["decision"])
        decisions_b.append(rb["result"]["adaptation"]["decision"])
        challenges_a.append(ra["research"]["next_challenge"]["challenge_id"])
        challenges_b.append(rb["research"]["next_challenge"]["challenge_id"])
        engine = service_a.tutor.get_trace(a["session_id"])[-1]
        assert ra["result"]["adaptation"]["decision"] == engine.decision.value
        if ra.get("demo", {}).get("complete"):
            break
    assert decisions_a == decisions_b
    assert challenges_a == challenges_b
    assert "INCREASE" in decisions_a
    assert "PROBE" in decisions_a
    assert "REMEDIATE" in decisions_a
    later = decisions_a[decisions_a.index("REMEDIATE") :]
    assert any(item != "REMEDIATE" for item in later[1:])


def test_demo_explanations_come_from_trace():
    service = make_service()
    view = service.start_demo()
    result = service.demo_step(view["session_id"])
    engine = service.tutor.get_trace(view["session_id"])[-1]
    assert result["result"]["adaptation"]["reason"] == engine.reason
    assert result["research"]["strategy"]["reason"] == engine.reason
