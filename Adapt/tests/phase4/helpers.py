"""Helpers for Phase 4 application-boundary tests."""

from __future__ import annotations

import json
import threading
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from adapt.product.errors import SessionCompleteError
from adapt.product.service import ProductService
from adapt.tutor.responses import build_scripted_response
from adapt.tutor.tutor import AdaptiveTutor, DEFAULT_SEED
from app.server import create_server


def make_service(seed: int = DEFAULT_SEED) -> ProductService:
    return ProductService(seed=seed)


def scripted_submit(service: ProductService, session_id: str, kind: str) -> dict[str, Any]:
    session = service.get_session(session_id)
    if session.get("complete") or not session.get("challenge"):
        raise SessionCompleteError("This session is complete.")
    challenge_id = session["challenge"]["challenge_id"]
    tutor_session = service.engine_session(session_id)
    response = build_scripted_response(
        tutor_session.current_challenge,
        kind,
        learner_id=tutor_session.learner_id,
        response_id=f"{session_id}-R-{tutor_session.step_number + 1:03d}",
    )
    return service.submit_response(
        session_id,
        answer=response.answer,
        confidence=response.learner_confidence.value,
        reasoning=response.reasoning,
        challenge_id=challenge_id,
    )


def run_kinds_through_product(
    kinds: tuple[str, ...] | list[str],
    *,
    topic_id: str = "algebra",
    session_id: str | None = None,
    learner_id: str = "L-P4",
    initial_challenge: str | None = "ALG-M-001",
    service: ProductService | None = None,
    max_steps: int | None = None,
) -> tuple[ProductService, dict[str, Any], list[dict[str, Any]]]:
    local = service or make_service()
    view = local.create_session(
        topic_id=topic_id,
        learner_id=learner_id,
        session_id=session_id,
        initial_challenge=initial_challenge,
        max_steps=max_steps or max(len(kinds), 1),
    )
    results = []
    for kind in kinds:
        results.append(scripted_submit(local, view["session_id"], kind))
    return local, local.get_session(view["session_id"]), results


def run_kinds_through_tutor(
    kinds: tuple[str, ...] | list[str],
    *,
    learner_id: str = "L-P3",
    session_id: str = "SES-P3",
    concept_id: str = "basic_algebra",
    initial_challenge: str | None = "ALG-M-001",
    seed: int = DEFAULT_SEED,
):
    tutor = AdaptiveTutor(seed=seed)
    tutor.start_session(
        learner_id=learner_id,
        concept_id=concept_id,
        session_id=session_id,
        initial_challenge=initial_challenge,
    )
    traces = []
    for index, kind in enumerate(kinds, start=1):
        challenge = tutor.get_next_challenge(session_id)
        response = build_scripted_response(
            challenge,
            kind,
            learner_id=learner_id,
            response_id=f"{session_id}-R-{index:03d}",
        )
        traces.append(tutor.submit_response(session_id, response))
    return tutor, tutor.get_session(session_id), traces


class LiveApp:
    def __init__(self, service: ProductService | None = None) -> None:
        self.service = service or make_service()
        self.server = create_server(host="127.0.0.1", port=0, service=self.service)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.port = self.server.server_address[1]
        self.base = f"http://127.0.0.1:{self.port}"

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()

    def request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = Request(
            self.base + path,
            data=data,
            method=method,
            headers={"Content-Type": "application/json"} if data else {},
        )
        try:
            with urlopen(request, timeout=10) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            body = json.loads(exc.read().decode("utf-8"))
            error = RuntimeError(body.get("message") or str(exc))
            error.code = body.get("error")  # type: ignore[attr-defined]
            error.status = exc.code  # type: ignore[attr-defined]
            error.payload = body  # type: ignore[attr-defined]
            raise error from exc
