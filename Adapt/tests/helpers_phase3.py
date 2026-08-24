"""Builders for Phase 3 tutor tests."""

from __future__ import annotations

from adapt.tutor.responses import build_scripted_response
from adapt.tutor.tutor import AdaptiveTutor, DEFAULT_SEED


def make_tutor(seed: int = DEFAULT_SEED) -> AdaptiveTutor:
    return AdaptiveTutor(seed=seed)


def run_kinds(
    kinds: tuple[str, ...] | list[str],
    *,
    learner_id: str = "L-P3",
    session_id: str = "SES-P3",
    concept_id: str = "basic_algebra",
    initial_challenge: str | None = "ALG-M-001",
    tutor: AdaptiveTutor | None = None,
    **start_kwargs,
):
    local = tutor or make_tutor()
    local.start_session(
        learner_id=learner_id,
        concept_id=concept_id,
        session_id=session_id,
        initial_challenge=initial_challenge,
        **start_kwargs,
    )
    traces = []
    for index, kind in enumerate(kinds, start=1):
        challenge = local.get_next_challenge(session_id)
        response = build_scripted_response(
            challenge,
            kind,
            learner_id=learner_id,
            response_id=f"{session_id}-R-{index:03d}",
        )
        traces.append(local.submit_response(session_id, response))
    return local, local.get_session(session_id), traces
