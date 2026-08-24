"""AdaptiveTutor — Phase 3 end-to-end orchestration.

Integrates evidence analysis, learner-state updates, strategy, and challenge
selection into one session-scoped adaptive loop.
"""

from __future__ import annotations

from typing import Any

from adapt.analysis.evidence_analyzer import EvidenceAnalyzer
from adapt.errors import InvalidLearnerResponseError, InvalidSessionError, SessionNotFoundError
from adapt.models.challenge import Challenge
from adapt.models.enums import LearnerConfidence, StrategyName, parse_enum
from adapt.models.learner_response import LearnerResponse
from adapt.models.learner_state import LearnerState, initial_learner_state
from adapt.models.strategy import StrategyState, initial_strategy_state
from adapt.pipeline import AdaptPipeline
from adapt.state.state_updater import StateUpdater
from adapt.strategy.engine import AdaptiveStrategyEngine
from adapt.tutor.challenge_bank import PHASE3_BANK, UNAVAILABLE_CHALLENGE, get_phase3_challenge
from adapt.tutor.explain import explain_session, explain_step
from adapt.tutor.selector import AdaptiveChallengeSelector
from adapt.tutor.session import StepTrace, TutorSession

DEFAULT_SEED = 20260814


class AdaptiveTutor:
    def __init__(
        self,
        *,
        bank: tuple[Challenge, ...] | None = None,
        seed: int = DEFAULT_SEED,
        analyzer: EvidenceAnalyzer | None = None,
        updater: StateUpdater | None = None,
        strategy_engine: AdaptiveStrategyEngine | None = None,
        selector: AdaptiveChallengeSelector | None = None,
    ) -> None:
        self.seed = int(seed)
        self.bank = bank if bank is not None else PHASE3_BANK
        self.selector = selector or AdaptiveChallengeSelector(bank=self.bank)
        self.pipeline = AdaptPipeline(
            analyzer=analyzer or EvidenceAnalyzer(),
            updater=updater or StateUpdater(),
            selector=self.selector,
            strategy_engine=strategy_engine or AdaptiveStrategyEngine(),
        )
        self._sessions: dict[str, TutorSession] = {}
        self._session_counter = 0
        self._bank_by_id = {item.challenge_id: item for item in self.bank}

    def start_session(
        self,
        *,
        learner_id: str,
        concept_id: str = "basic_algebra",
        session_id: str | None = None,
        initial_challenge: Challenge | str | None = None,
        learner_state: LearnerState | None = None,
        strategy_state: StrategyState | None = None,
        seed: int | None = None,
    ) -> TutorSession:
        if not learner_id:
            raise InvalidSessionError("learner_id is required")
        self._session_counter += 1
        resolved_id = session_id or f"SES-{self.seed}-{self._session_counter:04d}"
        if resolved_id in self._sessions:
            raise InvalidSessionError(f"session already exists: {resolved_id}")
        state = learner_state or initial_learner_state(learner_id, concept_id)
        if state.learner_id != learner_id:
            raise InvalidSessionError("learner_state.learner_id must match learner_id")
        strategy = strategy_state or initial_strategy_state()
        challenge = self._resolve_initial_challenge(concept_id, initial_challenge)
        session = TutorSession(
            session_id=resolved_id,
            learner_id=learner_id,
            concept_id=state.concept_id,
            current_challenge=challenge,
            learner_state=state,
            strategy_state=strategy,
            history=(),
            recent_evidence=(),
            used_challenge_ids=(challenge.challenge_id,),
            step_number=0,
            traces=(),
            seed=self.seed if seed is None else int(seed),
        )
        self._sessions[resolved_id] = session
        return session

    def submit_response(
        self,
        session_id: str,
        response: LearnerResponse | dict[str, Any],
    ) -> StepTrace:
        session = self._require(session_id)
        resolved = self._coerce_response(session, response)
        strategy_before = session.strategy_state
        state_before = session.learner_state
        challenge = session.current_challenge
        pipeline_trace = self.pipeline.run(
            learner_state=state_before,
            challenge=challenge,
            response=resolved,
            history=list(session.history),
            recent_evidence=list(session.recent_evidence),
            used_challenge_ids=list(session.used_challenge_ids),
            interaction_id=f"{session.session_id}-I-{session.step_number + 1:03d}",
            strategy_state=strategy_before,
        )
        strategy_after = pipeline_trace.strategy_state or strategy_before
        decision = (
            pipeline_trace.strategy_decision.decision
            if pipeline_trace.strategy_decision is not None
            else StrategyName.GATHER_EVIDENCE
        )
        reason = (
            pipeline_trace.strategy_decision.reason
            if pipeline_trace.strategy_decision is not None
            else "Evidence was processed; additional evidence is required."
        )
        reason_codes = (
            pipeline_trace.strategy_decision.reason_codes
            if pipeline_trace.strategy_decision is not None
            else ("gather_evidence",)
        )
        evidence_ids = (
            pipeline_trace.strategy_decision.evidence_ids
            if pipeline_trace.strategy_decision is not None
            else (resolved.response_id,)
        )
        step_number = session.step_number + 1
        used = session.used_challenge_ids
        next_id = pipeline_trace.next_challenge.challenge_id
        if next_id not in used:
            used = used + (next_id,)
        step = StepTrace(
            step_number=step_number,
            session_id=session.session_id,
            challenge_id=challenge.challenge_id,
            response=resolved,
            evidence=pipeline_trace.evidence,
            state_before=state_before,
            state_after=pipeline_trace.learner_state_after,
            strategy_before=strategy_before,
            strategy_after=strategy_after,
            decision=decision,
            adaptation_action=pipeline_trace.adaptation_decision.decision,
            reason=reason,
            reason_codes=reason_codes,
            evidence_ids=evidence_ids,
            next_challenge_id=next_id,
            next_challenge=pipeline_trace.next_challenge,
            challenge=challenge,
            explanation="",
            pipeline_trace=pipeline_trace,
        )
        step = StepTrace(
            step_number=step.step_number,
            session_id=step.session_id,
            challenge_id=step.challenge_id,
            response=step.response,
            evidence=step.evidence,
            state_before=step.state_before,
            state_after=step.state_after,
            strategy_before=step.strategy_before,
            strategy_after=step.strategy_after,
            decision=step.decision,
            adaptation_action=step.adaptation_action,
            reason=step.reason,
            reason_codes=step.reason_codes,
            evidence_ids=step.evidence_ids,
            next_challenge_id=step.next_challenge_id,
            next_challenge=step.next_challenge,
            challenge=step.challenge,
            explanation=explain_step(step),
            pipeline_trace=step.pipeline_trace,
        )
        updated = TutorSession(
            session_id=session.session_id,
            learner_id=session.learner_id,
            concept_id=session.concept_id,
            current_challenge=pipeline_trace.next_challenge,
            learner_state=pipeline_trace.learner_state_after,
            strategy_state=strategy_after,
            history=session.history + (resolved,),
            recent_evidence=session.recent_evidence + (pipeline_trace.evidence,),
            used_challenge_ids=used,
            step_number=step_number,
            traces=session.traces + (step,),
            seed=session.seed,
        )
        self._sessions[session_id] = updated
        return step

    def get_next_challenge(self, session_id: str) -> Challenge:
        return self._require(session_id).current_challenge

    def get_state(self, session_id: str) -> LearnerState:
        return self._require(session_id).learner_state

    def get_strategy(self, session_id: str) -> StrategyState:
        return self._require(session_id).strategy_state

    def get_trace(self, session_id: str) -> tuple[StepTrace, ...]:
        return self._require(session_id).traces

    def get_session(self, session_id: str) -> TutorSession:
        return self._require(session_id)

    def explain(self, session_id: str, step_number: int | None = None) -> str:
        return explain_session(self._require(session_id), step_number)

    def snapshot(self, session_id: str) -> dict[str, Any]:
        session = self._require(session_id)
        return {
            "session": session.to_dict(),
            "seed": session.seed,
            "bank_ids": [item.challenge_id for item in self.bank],
        }

    def restore(self, snapshot: dict[str, Any]) -> TutorSession:
        if not isinstance(snapshot, dict) or "session" not in snapshot:
            raise InvalidSessionError("snapshot must contain a session object")
        session = TutorSession.from_dict(snapshot["session"])
        self._sessions[session.session_id] = session
        return session

    def _require(self, session_id: str) -> TutorSession:
        session = self._sessions.get(session_id)
        if session is None:
            raise SessionNotFoundError(f"unknown session: {session_id}")
        return session

    def _resolve_initial_challenge(
        self,
        concept_id: str,
        initial_challenge: Challenge | str | None,
    ) -> Challenge:
        if isinstance(initial_challenge, Challenge):
            return initial_challenge
        if isinstance(initial_challenge, str):
            if initial_challenge in self._bank_by_id:
                return self._bank_by_id[initial_challenge]
            try:
                return get_phase3_challenge(initial_challenge)
            except KeyError as exc:
                raise InvalidSessionError(f"unknown challenge: {initial_challenge}") from exc
        matching = [item for item in self.bank if item.concept_id == concept_id]
        if not matching:
            matching = list(self.bank)
        if not matching:
            return UNAVAILABLE_CHALLENGE
        easy_diag = [
            item
            for item in matching
            if item.challenge_type.value in {"DIAGNOSTIC", "PROBE"} and item.difficulty.value == "EASY"
        ]
        if easy_diag:
            return easy_diag[0]
        easy = [item for item in matching if item.difficulty.value == "EASY"]
        return (easy or matching)[0]

    def _coerce_response(
        self,
        session: TutorSession,
        response: LearnerResponse | dict[str, Any],
    ) -> LearnerResponse:
        if isinstance(response, LearnerResponse):
            if response.challenge_id != session.current_challenge.challenge_id:
                raise InvalidLearnerResponseError(
                    "response.challenge_id does not match the current challenge"
                )
            return response
        if not isinstance(response, dict):
            raise InvalidLearnerResponseError("response must be a LearnerResponse or object")
        raw_confidence = response.get("learner_confidence", LearnerConfidence.UNKNOWN)
        if raw_confidence is None:
            raw_confidence = LearnerConfidence.UNKNOWN
        response_id = response.get("response_id") or f"{session.session_id}-R-{session.step_number + 1:03d}"
        return LearnerResponse(
            response_id=str(response_id),
            learner_id=str(response.get("learner_id") or session.learner_id),
            concept_id=str(response.get("concept_id") or session.concept_id),
            challenge_id=str(response.get("challenge_id") or session.current_challenge.challenge_id),
            answer="" if response.get("answer") is None else str(response.get("answer")),
            reasoning=response.get("reasoning"),
            learner_confidence=parse_enum(
                raw_confidence,
                LearnerConfidence,
                field_name="learner_confidence",
                error_cls=InvalidLearnerResponseError,
            ),
            timestamp=response.get("timestamp"),
            response_time=response.get("response_time"),
            metadata=response.get("metadata"),
        )
