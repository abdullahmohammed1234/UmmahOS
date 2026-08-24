"""Lightweight challenge experience around AdaptiveTutor."""

from tests.phase4.helpers import make_service


def test_answer_confidence_optional_reasoning():
    service = make_service()
    view = service.create_session(
        topic_id="csafety-coded",
        concept_id="csafety_coded_recognition",
        session_id="P8-CH-001",
        max_steps=2,
    )
    plan = view["evidence_plan"]
    assert plan["ask_confidence"] is True
    assert plan["reasoning_optional"] is True
    assert plan["reasoning_prompt"] == "How did you approach it?"
    assert "Optional" in plan["reasoning_help"]
    ids = {item["id"] for item in plan["approach_options"]}
    assert ids == {"knew", "worked", "pattern", "guessed", "unsure"}
    visual = plan["confidence_visual"]
    assert [item["value"] for item in visual] == [1, 3, 4, 5]
    assert view["confidence_scale"][0]["value"] == 1
    assert view["confidence_scale"][-1]["value"] == 5
    answer = (
        view["challenge"].get("choices", ["The phrase may carry coded meaning even if it looks neutral to outsiders"])[0]
        if view["challenge"].get("choices")
        else "The phrase may carry coded meaning even if it looks neutral to outsiders"
    )
    result = service.submit_response(
        view["session_id"],
        answer=answer,
        confidence=4,
        approach="knew",
        explanation="",
        challenge_id=view["challenge"]["challenge_id"],
    )
    assert result["result"]["feedback"]
    assert result["result"]["explanation"]["from_trace"] is True


def test_concept_session_starts_without_essay():
    service = make_service()
    view = service.create_session(
        concept_id="csafety_context_preservation",
        subject_id="community-safety",
        session_id="P8-CH-002",
        max_steps=2,
    )
    assert view["challenge"]["prompt"]
    assert "expected_answer" not in view["challenge"]
    answer = (
        view["challenge"].get("choices", ["Preserve the surrounding conversation context before deciding how to respond or report"])[0]
        if view["challenge"].get("choices")
        else "Preserve the surrounding conversation context before deciding how to respond or report"
    )
    result = service.submit_response(
        view["session_id"],
        answer=answer,
        confidence=1,
        challenge_id=view["challenge"]["challenge_id"],
    )
    assert result["progress"]["completed"] == 1
    assert result["result"]["adaptation"]["decision"]
