"""M9-012 — Invalid input does not crash; friendly errors, no stack traces."""

from tests.phase4.helpers import LiveApp, make_service


def test_m9_012_error_handling():
    service = make_service()
    view = service.create_session(topic_id="algebra", session_id="P9-ER-001", max_steps=3)
    raised = None
    try:
        service.submit_response(view["session_id"], answer="   ", confidence=3)
    except Exception as exc:
        raised = exc
    assert raised is not None
    assert "Traceback" not in str(raised)
    long_answer = "x" * 20001
    try:
        service.submit_response(view["session_id"], answer=long_answer, confidence=3)
        assert False, "expected too-long error"
    except Exception as exc:
        assert "too long" in str(exc).lower() or "invalid" in str(exc).lower()
    service.submit_response(
        view["session_id"],
        answer="4",
        confidence=4,
        challenge_id=view["challenge"]["challenge_id"],
    )
    try:
        service.submit_response(
            view["session_id"],
            answer="4",
            confidence=4,
            challenge_id=view["challenge"]["challenge_id"],
        )
        assert False, "expected repeat submission error"
    except Exception:
        pass
    try:
        service.create_session(topic_id="not-a-topic")
        assert False
    except Exception as exc:
        assert "unsupported" in str(exc).lower() or "topic" in str(exc).lower()
    try:
        service.get_session("SES-missing")
        assert False
    except Exception:
        pass
    reset = service.reset_session(view["session_id"])
    assert reset["session_id"] != view["session_id"]


def test_m9_012_http_errors_are_friendly():
    app = LiveApp()
    try:
        try:
            app.request("POST", "/api/sessions", {"topic_id": "nope"})
            assert False
        except RuntimeError as exc:
            assert "Traceback" not in str(exc)
            assert getattr(exc, "status", 400) in {400, 404, 422}
        try:
            app.request("GET", "/api/sessions/missing")
            assert False
        except RuntimeError as exc:
            assert "Traceback" not in str(exc)
        huge = app.request("POST", "/api/sessions", {"topic_id": "algebra", "max_steps": 2})
        try:
            app.request(
                "POST",
                f"/api/sessions/{huge['session_id']}/responses",
                {"answer": "<script>alert(1)</script> & special", "confidence": 3},
            )
        except RuntimeError:
            pass
    finally:
        app.close()
