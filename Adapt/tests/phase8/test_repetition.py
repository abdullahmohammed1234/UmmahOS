"""Repetition avoidance remains a selector concern, not a UI override."""

from tests.phase4.helpers import make_service, scripted_submit


def test_consecutive_challenges_vary_when_bank_allows():
    service = make_service()
    view = service.create_session(
        topic_id="csafety-context",
        session_id="P8-RP-001",
        initial_challenge="CSAFE-CTX-001",
        max_steps=6,
    )
    seen = [view["challenge"]["challenge_id"]]
    for kind in ("strong_correct", "weak_correct", "strong_correct", "misconception"):
        result = scripted_submit(service, view["session_id"], kind)
        nxt = result["result"]["next_challenge"]["challenge_id"]
        seen.append(nxt)
        if result["complete"]:
            break
    consecutive_same = sum(1 for i in range(1, len(seen)) if seen[i] == seen[i - 1] and seen[i] != "UNAVAILABLE")
    assert consecutive_same == 0
    assert len(set(seen)) >= 2
