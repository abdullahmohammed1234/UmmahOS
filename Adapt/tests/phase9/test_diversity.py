"""M9-004 — Repeated challenges are avoided according to the rotation policy."""

from adapt.product.rotation import RECENT_WINDOW, filter_repeats, should_avoid_repeat
from adapt.models.enums import StrategyName
from adapt.history.memory import ChallengeHistory
from tests.phase4.helpers import make_service, scripted_submit


def test_m9_004_challenge_diversity():
    service = make_service()
    view = service.create_session(
        topic_id="csafety-context",
        session_id="P9-DV-001",
        initial_challenge="CSAFE-CTX-001",
        max_steps=8,
    )
    seen = [view["challenge"]["challenge_id"]]
    for kind in ("strong_correct", "weak_correct", "strong_correct", "misconception", "strong_correct"):
        session = service.get_session(view["session_id"])
        if session.get("complete"):
            break
        result = scripted_submit(service, view["session_id"], kind)
        nxt = result["result"]["next_challenge"]["challenge_id"]
        seen.append(nxt)
        if result["complete"]:
            break
    consecutive_same = sum(
        1 for i in range(1, len(seen)) if seen[i] == seen[i - 1] and seen[i] != "UNAVAILABLE"
    )
    assert consecutive_same == 0
    assert len(set(item for item in seen if item != "UNAVAILABLE")) >= 3
    recent = service.get_session(view["session_id"])["recent_challenge_ids"]
    assert recent
    assert len(recent) <= max(len(seen), RECENT_WINDOW + 1)


def test_m9_004_policy_filters_recent_ids():
    history = ChallengeHistory()
    history.from_used_ids(["CSAFE-CTX-001", "CSAFE-CTX-002"], lookup=lambda cid: type("M", (), {"concept_id": "c", "difficulty": 2, "challenge_type": "DIRECT", "family": cid})())
    class Item:
        def __init__(self, cid):
            self.id = cid
            self.family = cid
            self.challenge_type = "DIRECT"
    pool = [Item("CSAFE-CTX-001"), Item("CSAFE-CTX-005")]
    filtered = filter_repeats(pool, history, strategy=StrategyName.MAINTAIN, current_id="CSAFE-CTX-002")
    assert all(item.id != "CSAFE-CTX-001" for item in filtered) or len(pool) == 1
    assert should_avoid_repeat(StrategyName.INCREASE)
    assert not should_avoid_repeat(StrategyName.REMEDIATE)
