"""Phase 4 application boundary.

The frontend and demo talk to ProductService. AdaptiveTutor remains the only
source of evidence, state, strategy, and next-challenge decisions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import RLock
from typing import Any
from uuid import uuid4

from adapt.errors import (
    AdaptError,
    InvalidLearnerResponseError,
    InvalidSessionError,
    SessionNotFoundError,
)
from adapt.content.catalog import CATALOG
from adapt.product.confidence import scale_options, to_engine_confidence
from adapt.product.content import product_content
from adapt.product.counterfactual import default_counterfactual
from adapt.product.demo import load_demo_scenario
from adapt.product.errors import (
    ChallengeUnavailableError,
    InvalidResponseError,
    SessionCompleteError,
    SessionUnavailableError,
    SubmissionError,
)
from adapt.product.explanations import learner_adaptation_chain, learner_explanation
from adapt.product.experience import (
    attempt_from_step,
    combine_reasoning,
    evidence_plan,
    learner_progress_view,
    public_challenge,
    session_insights,
    session_journey,
    what_adapt_noticed,
    why_this_question,
)
from adapt.product.journey import catalog_journey
from adapt.product.labels import (
    DEMO_SCENARIO_LABEL,
    PROMISE_SHORT,
    learner_strategy_plain,
    opening_state,
    strategy_label,
)
from adapt.product.present import (
    adaptation_from_step,
    chain_link,
    feedback_from_evidence,
    timeline_from_session,
    understanding_view,
)
from adapt.product.presentation import challenge_presentation, subject_theme
from adapt.product.progress import concept_status_view, recommend_concept_id, subject_progress_row
from adapt.product.recommendations import recommend_for_subject
from adapt.product.story import adaptation_story
from adapt.product.summary import session_summary
from adapt.product.topics import TOPICS_BY_ID, list_topics, topic_for_concept
from adapt.product.trace_explain import human_trace_explanation
from adapt.selection.selector import Phase7ChallengeSelector
from adapt.tutor.responses import build_scripted_response
from adapt.tutor.tutor import DEFAULT_SEED, AdaptiveTutor

DEFAULT_MAX_STEPS = 10
MAX_TEXT_LENGTH = 20000


def _evidence_source_label(source: str | None) -> str | None:
    """Learner-facing label. Fallback must never be presented as an LLM result."""
    from adapt.llm.fallback import LIVE_EVIDENCE_SOURCES, SOURCE_FALLBACK

    if source in LIVE_EVIDENCE_SOURCES:
        return "AI-assisted evidence analysis"
    if source == SOURCE_FALLBACK:
        return "Deterministic fallback evidence analysis"
    return None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ProductSession:
    session_id: str
    topic_id: str
    max_steps: int
    mode: str
    created_at: str
    analytics: list[dict[str, Any]] = field(default_factory=list)
    last_submission_key: str | None = None
    demo_kinds: tuple[str, ...] = ()
    demo_index: int = 0
    demo_id: str | None = None
    runtime: str = "core"
    subject_id: str | None = None
    learner_id: str | None = None
    history: list[dict[str, Any]] = field(default_factory=list)
    last_selection: dict[str, Any] | None = None
    concept_id: str | None = None
    last_workflow: dict[str, Any] | None = None
    llm_enabled: bool = False


class ProductService:
    """Local service boundary around AdaptiveTutor. No independent adaptation."""

    def __init__(
        self,
        *,
        tutor: AdaptiveTutor | None = None,
        seed: int = DEFAULT_SEED,
        llm_client=None,
        use_gemini: bool = False,
        gemini_prompt_id: str | None = None,
    ) -> None:
        self.seed = int(seed)
        self._llm_analyzer = None
        if llm_client is not None or use_gemini:
            from adapt.llm.analyzer import LLMEvidenceAnalyzer

            self._llm_analyzer = LLMEvidenceAnalyzer(
                client=llm_client,
                prompt_id=gemini_prompt_id,
            )
        self.tutor = tutor or AdaptiveTutor(seed=self.seed, analyzer=self._llm_analyzer)
        self._experience_selector = Phase7ChallengeSelector(catalog=CATALOG)
        self._experience_tutor = AdaptiveTutor(
            bank=CATALOG.engine_bank,
            selector=self._experience_selector,
            seed=self.seed,
            analyzer=self._llm_analyzer,
        )
        self._meta: dict[str, ProductSession] = {}
        self._progress: dict[str, dict[str, float]] = {}
        self._activity: dict[str, dict[str, dict[str, Any]]] = {}
        self._lock = RLock()

    def list_topics(self) -> list[dict[str, Any]]:
        return list_topics()

    def list_subjects(self, *, learner_id: str | None = None) -> list[dict[str, Any]]:
        mastery = dict(self._progress.get(learner_id or "", {}) or {})
        activity = dict(self._activity.get(learner_id or "", {}) or {})
        rows = []
        for subject in CATALOG.subjects:
            row = subject_progress_row(
                subject.subject_id,
                concept_mastery=mastery,
                activity=activity,
            )
            rows.append(row)
        return rows

    def get_subject(self, subject_id: str, *, learner_id: str | None = None) -> dict[str, Any]:
        subject = CATALOG.subject(subject_id)
        if subject is None:
            raise InvalidResponseError(f"unsupported subject: {subject_id}")
        learner_mastery = dict(self._progress.get(learner_id or "", {}) or {})
        activity = dict(self._activity.get(learner_id or "", {}) or {})
        topics = []
        for topic in CATALOG.topics_for_subject(subject_id):
            values = [
                learner_mastery[cid]
                for cid in topic.concept_ids
                if cid in learner_mastery
            ]
            topics.append(
                topic.to_dict(
                    mastery=sum(values) / len(values) if values else None,
                    challenge_count=len(CATALOG.challenges_for_topic(topic.topic_id)),
                )
            )
        concepts = []
        recommended_id = recommend_concept_id(subject_id, learner_mastery, activity)
        for item in CATALOG.concepts_for_subject(subject_id):
            info = activity.get(item.concept_id) or {}
            concepts.append(
                concept_status_view(
                    item,
                    mastery=learner_mastery.get(item.concept_id),
                    attempts=int(info.get("attempts") or 0),
                    last_correct=info.get("last_correct"),
                    recommended=item.concept_id == recommended_id,
                )
            )
        payload = subject.to_dict(concept_count=len(concepts), topic_count=len(topics))
        payload.update(
            subject_progress_row(
                subject_id,
                concept_mastery=learner_mastery,
                activity=activity,
            )
        )
        payload["topics"] = topics
        payload["concepts"] = concepts
        payload["recommended"] = recommend_for_subject(
            subject_id,
            concept_mastery=learner_mastery,
            activity=activity,
        )
        payload["theme"] = subject_theme(subject_id)
        return payload

    def confidence_scale(self) -> list[dict[str, int | str]]:
        return scale_options()

    def content(self) -> dict[str, Any]:
        payload = product_content()
        payload["catalog"] = CATALOG.metrics()
        from adapt.product.rotation import POLICY, RECENT_WINDOW

        payload["rotation"] = {"window": RECENT_WINDOW, "policy": POLICY}
        return payload

    def _resolve_topic(self, topic_id: str):
        if topic_id in TOPICS_BY_ID:
            spec = CATALOG.topic(topic_id)
            return TOPICS_BY_ID[topic_id], "core", spec
        spec = CATALOG.topic(topic_id)
        if spec is None:
            raise InvalidResponseError(f"unsupported topic: {topic_id}")
        runtime = "core" if spec.legacy else "experience"
        return spec.as_topic(), runtime, spec

    def _tutor_for(self, meta: ProductSession) -> AdaptiveTutor:
        if meta.runtime == "experience":
            return self._experience_tutor
        return self.tutor

    def create_session(
        self,
        *,
        topic_id: str = "",
        learner_id: str | None = None,
        max_steps: int = DEFAULT_MAX_STEPS,
        mode: str = "learner",
        session_id: str | None = None,
        initial_challenge: str | None = None,
        subject_id: str | None = None,
        concept_id: str | None = None,
    ) -> dict[str, Any]:
        if concept_id:
            concept = CATALOG.concept(str(concept_id))
            if concept is None:
                raise InvalidResponseError(f"unsupported concept: {concept_id}")
            topic_id = concept.topic_id
            subject_id = subject_id or concept.subject_id
            if not initial_challenge:
                options = CATALOG.challenges_for_concept(concept.concept_id)
                if options:
                    initial_challenge = options[0].id
        if not topic_id:
            raise InvalidResponseError("topic_id or concept_id is required")
        topic, runtime, spec = self._resolve_topic(topic_id)
        resolved_learner = learner_id or f"learner-{uuid4().hex[:8]}"
        resolved_id = session_id or f"SES-{self.seed}-{uuid4().hex[:8]}"
        challenge_id = initial_challenge or topic.initial_challenge
        engine_concept = str(concept_id or topic.concept_id)
        tutor = self.tutor if runtime == "core" else self._experience_tutor
        try:
            session = tutor.start_session(
                learner_id=resolved_learner,
                concept_id=engine_concept,
                session_id=resolved_id,
                initial_challenge=challenge_id,
            )
        except InvalidSessionError as exc:
            raise SessionUnavailableError(str(exc)) from exc
        if session.current_challenge.challenge_id == "UNAVAILABLE":
            raise ChallengeUnavailableError("No challenge is currently available.")
        meta = ProductSession(
            session_id=session.session_id,
            topic_id=topic.topic_id,
            max_steps=max(1, int(max_steps)),
            mode=mode,
            created_at=_now(),
            runtime=runtime,
            subject_id=subject_id or (spec.subject_id if spec else None),
            learner_id=resolved_learner,
            concept_id=str(concept_id or topic.concept_id),
            llm_enabled=self._llm_analyzer is not None,
        )
        with self._lock:
            self._meta[session.session_id] = meta
        return self.get_session(session.session_id)

    def get_session(self, session_id: str) -> dict[str, Any]:
        session, meta = self._require(session_id)
        return self._session_view(session, meta)

    def submit_response(
        self,
        session_id: str,
        *,
        answer: str | None,
        confidence: int | str | None,
        reasoning: str | None = None,
        challenge_id: str | None = None,
        approach: str | None = None,
        explanation: str | None = None,
    ) -> dict[str, Any]:
        with self._lock:
            session, meta = self._require(session_id)
            tutor = self._tutor_for(meta)
            if session.step_number >= meta.max_steps:
                raise SessionCompleteError("This session is complete.")
            if answer is None or not str(answer).strip():
                raise InvalidResponseError("answer is required")
            if len(str(answer)) > MAX_TEXT_LENGTH:
                raise InvalidResponseError("answer is too long")
            combined = combine_reasoning(approach, explanation if explanation is not None else reasoning)
            if combined is not None and len(combined) > MAX_TEXT_LENGTH:
                raise InvalidResponseError("reasoning is too long")
            if reasoning is not None and len(str(reasoning)) > MAX_TEXT_LENGTH:
                raise InvalidResponseError("reasoning is too long")
            engine_confidence = to_engine_confidence(confidence)
            current = session.current_challenge
            if current.challenge_id == "UNAVAILABLE":
                raise ChallengeUnavailableError("No challenge is currently available.")
            if challenge_id and challenge_id != current.challenge_id:
                raise InvalidResponseError("challenge_id does not match the current challenge")
            submission_key = f"{session.step_number}:{current.challenge_id}"
            if meta.last_submission_key == submission_key:
                raise InvalidResponseError("this challenge was already submitted")
            payload = {
                "answer": str(answer).strip(),
                "learner_confidence": engine_confidence.value,
                "reasoning": combined if combined is not None else (
                    None if reasoning is None else str(reasoning).strip() or None
                ),
                "challenge_id": current.challenge_id,
                "learner_id": session.learner_id,
                "concept_id": session.concept_id,
                "metadata": {
                    "approach": approach,
                    "explanation": explanation if explanation is not None else reasoning,
                },
            }
            try:
                step = tutor.submit_response(session_id, payload)
            except InvalidLearnerResponseError as exc:
                raise InvalidResponseError(str(exc)) from exc
            except SessionNotFoundError as exc:
                raise SessionUnavailableError(str(exc)) from exc
            except AdaptError as exc:
                raise SubmissionError(str(exc)) from exc
            meta.last_submission_key = submission_key
            attempt = attempt_from_step(step, session_id=session_id)
            meta.history.append(attempt.to_dict())
            if self._llm_analyzer is not None and self._llm_analyzer.last_result is not None:
                workflow = self._llm_analyzer.last_result
                meta.last_workflow = workflow.to_dict()
                meta.history[-1]["llm_workflow"] = meta.last_workflow
                meta.history[-1]["evidence_source"] = workflow.source
            if meta.runtime == "experience" and self._experience_selector.last_result is not None:
                meta.last_selection = self._experience_selector.last_result.to_dict()
            learner_key = meta.learner_id or session.learner_id
            self._progress.setdefault(learner_key, {})[step.state_after.concept_id] = (
                step.state_after.mastery_estimate
            )
            info = self._activity.setdefault(learner_key, {}).setdefault(
                step.state_after.concept_id,
                {"attempts": 0, "last_correct": None},
            )
            info["attempts"] = int(info.get("attempts") or 0) + 1
            info["last_correct"] = step.evidence.answer_status.value == "CORRECT"
            info["last_strategy"] = step.decision.value
        meta.analytics.append(
            {
                "step": step.step_number,
                "challenge": step.challenge_id,
                "response_id": step.response.response_id,
                "strategy": step.decision.value,
                "state_mastery": step.state_after.mastery_estimate,
                "timestamp": _now(),
            }
        )
        updated, meta = self._require(session_id)
        return self._step_result_view(updated, meta, include_research=True)

    def get_trace(self, session_id: str) -> dict[str, Any]:
        session, meta = self._require(session_id)
        return self._trace_view(session, meta)

    def get_summary(self, session_id: str) -> dict[str, Any]:
        session, meta = self._require(session_id)
        payload = session_summary(session, max_steps=meta.max_steps)
        payload["session_id"] = session.session_id
        payload["topic"] = self._resolve_topic(meta.topic_id)[0].to_dict()
        payload["complete"] = session.step_number >= meta.max_steps
        payload["story"] = adaptation_story(session)
        payload["insights"] = session_insights(session)
        payload["journey"] = session_journey(session)
        return payload

    def get_story(self, session_id: str) -> dict[str, Any]:
        session, _meta = self._require(session_id)
        return adaptation_story(session)

    def snapshot(self, session_id: str) -> dict[str, Any]:
        session, meta = self._require(session_id)
        tutor = self._tutor_for(meta)
        return {
            "tutor": tutor.snapshot(session.session_id),
            "product": {
                "session_id": meta.session_id,
                "topic_id": meta.topic_id,
                "max_steps": meta.max_steps,
                "mode": meta.mode,
                "created_at": meta.created_at,
                "analytics": list(meta.analytics),
                "last_submission_key": meta.last_submission_key,
                "demo_kinds": list(meta.demo_kinds),
                "demo_index": meta.demo_index,
                "demo_id": meta.demo_id,
                "runtime": meta.runtime,
                "subject_id": meta.subject_id,
                "learner_id": meta.learner_id,
                "history": list(meta.history),
                "last_selection": meta.last_selection,
                "concept_id": meta.concept_id,
                "last_workflow": meta.last_workflow,
                "llm_enabled": meta.llm_enabled,
            },
        }

    def restore(self, snapshot: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(snapshot, dict) or "tutor" not in snapshot or "product" not in snapshot:
            raise SessionUnavailableError("snapshot must contain tutor and product objects")
        product = snapshot["product"]
        runtime = str(product.get("runtime") or "core")
        tutor = self.tutor if runtime == "core" else self._experience_tutor
        try:
            session = tutor.restore(snapshot["tutor"])
        except InvalidSessionError as exc:
            raise SessionUnavailableError(str(exc)) from exc
        meta = ProductSession(
            session_id=session.session_id,
            topic_id=str(product.get("topic_id") or "algebra"),
            max_steps=int(product.get("max_steps") or DEFAULT_MAX_STEPS),
            mode=str(product.get("mode") or "learner"),
            created_at=str(product.get("created_at") or _now()),
            analytics=list(product.get("analytics") or []),
            last_submission_key=product.get("last_submission_key"),
            demo_kinds=tuple(product.get("demo_kinds") or ()),
            demo_index=int(product.get("demo_index") or 0),
            demo_id=product.get("demo_id"),
            runtime=runtime,
            subject_id=product.get("subject_id"),
            learner_id=product.get("learner_id"),
            history=list(product.get("history") or []),
            last_selection=product.get("last_selection"),
            concept_id=product.get("concept_id"),
            last_workflow=product.get("last_workflow"),
            llm_enabled=bool(product.get("llm_enabled")),
        )
        with self._lock:
            self._meta[session.session_id] = meta
        return self.get_session(session.session_id)

    def start_demo(self, *, scenario: dict[str, Any] | None = None) -> dict[str, Any]:
        spec = scenario or load_demo_scenario()
        view = self.create_session(
            topic_id=str(spec.get("topic_id") or "algebra"),
            learner_id="demo-learner",
            max_steps=int(spec.get("max_steps") or len(spec.get("responses") or [])),
            mode="demo",
            initial_challenge=spec.get("initial_challenge"),
        )
        session_id = view["session_id"]
        kinds = tuple(item["kind"] for item in spec.get("responses") or [])
        with self._lock:
            meta = self._meta[session_id]
            meta.demo_kinds = kinds
            meta.demo_index = 0
            meta.demo_id = str(spec.get("id") or "demo")
        view["demo"] = {
            "id": spec.get("id"),
            "title": spec.get("title"),
            "beats": spec.get("beats") or [],
            "total_steps": len(kinds),
            "next_index": 0,
            "label": DEMO_SCENARIO_LABEL,
            "seed": self.seed,
        }
        return view

    def demo_step(self, session_id: str) -> dict[str, Any]:
        session, meta = self._require(session_id)
        if meta.demo_index >= len(meta.demo_kinds):
            raise SessionCompleteError("The demo has no further scripted steps.")
        kind = meta.demo_kinds[meta.demo_index]
        challenge = session.current_challenge
        scripted = build_scripted_response(
            challenge,
            kind,
            learner_id=session.learner_id,
            response_id=f"{session.session_id}-DEMO-{meta.demo_index + 1:03d}",
        )
        result = self.submit_response(
            session_id,
            answer=scripted.answer,
            confidence=scripted.learner_confidence.value,
            reasoning=scripted.reasoning,
            challenge_id=challenge.challenge_id,
        )
        meta.demo_index += 1
        result["demo"] = {
            "kind": kind,
            "next_index": meta.demo_index,
            "total_steps": len(meta.demo_kinds),
            "complete": meta.demo_index >= len(meta.demo_kinds),
            "label": DEMO_SCENARIO_LABEL,
        }
        return result

    def run_counterfactual(self, spec: dict[str, Any] | None = None) -> dict[str, Any]:
        config = spec or default_counterfactual()
        challenge_id = str(config.get("challenge_id") or "ALG-M-001")
        concept_id = str(config.get("concept_id") or "basic_algebra")
        topic = topic_for_concept(concept_id)
        topic_id = topic.topic_id if topic else "algebra"
        learner_a = config.get("learner_a") or {}
        learner_b = config.get("learner_b") or {}
        kinds_a = tuple(learner_a.get("kinds") or ("strong_correct",) * 3)
        kinds_b = tuple(learner_b.get("kinds") or ("weak_correct",) * 3)
        run_a = self._scripted_run(
            topic_id=topic_id,
            learner_id="cf-a",
            kinds=kinds_a,
            initial_challenge=challenge_id,
            mode="research",
        )
        run_b = self._scripted_run(
            topic_id=topic_id,
            learner_id="cf-b",
            kinds=kinds_b,
            initial_challenge=challenge_id,
            mode="research",
        )
        a_final = run_a["trace"]["chain"][-1] if run_a["trace"]["chain"] else {}
        b_final = run_b["trace"]["chain"][-1] if run_b["trace"]["chain"] else {}
        a_first = run_a["trace"]["chain"][0] if run_a["trace"]["chain"] else {}
        start_challenge = a_first.get("challenge") or {
            "challenge_id": challenge_id,
            "prompt": "",
        }
        differentiated = (
            (a_final.get("strategy") or {}).get("decision")
            != (b_final.get("strategy") or {}).get("decision")
            or (a_final.get("next_challenge") or {}).get("challenge_id")
            != (b_final.get("next_challenge") or {}).get("challenge_id")
            or abs(
                float((a_final.get("state") or {}).get("mastery") or 0)
                - float((b_final.get("state") or {}).get("mastery") or 0)
            )
            >= 0.02
        )
        a_explain = a_final.get("human_explanation") or {}
        b_explain = b_final.get("human_explanation") or {}
        return {
            "id": config.get("id") or "counterfactual",
            "title": config.get("title") or "Same challenge, different evidence",
            "challenge": start_challenge,
            "learner_a": {
                "label": learner_a.get("label") or "Learner A",
                "summary": learner_a.get("summary") or "Correct · Strong reasoning · High confidence",
                "kinds": list(kinds_a),
                "session": run_a["session"],
                "trace": run_a["trace"],
                "final_decision": (a_final.get("strategy") or {}).get("decision"),
                "final_decision_label": strategy_label(
                    (a_final.get("strategy") or {}).get("decision") or "ASSESS"
                ),
                "final_decision_plain": learner_strategy_plain(
                    (a_final.get("strategy") or {}).get("decision") or "ASSESS"
                ),
                "evidence_summary": learner_a.get("summary") or "Correct · Strong reasoning · High confidence",
                "final_challenge": (a_final.get("next_challenge") or {}).get("challenge_id"),
                "final_mastery": (a_final.get("state") or {}).get("mastery"),
                "explanation": a_explain,
            },
            "learner_b": {
                "label": learner_b.get("label") or "Learner B",
                "summary": learner_b.get("summary") or "Correct · Weak reasoning · Low confidence",
                "kinds": list(kinds_b),
                "session": run_b["session"],
                "trace": run_b["trace"],
                "final_decision": (b_final.get("strategy") or {}).get("decision"),
                "final_decision_label": strategy_label(
                    (b_final.get("strategy") or {}).get("decision") or "ASSESS"
                ),
                "final_decision_plain": learner_strategy_plain(
                    (b_final.get("strategy") or {}).get("decision") or "ASSESS"
                ),
                "evidence_summary": learner_b.get("summary") or "Correct · Weak reasoning · Low confidence",
                "final_challenge": (b_final.get("next_challenge") or {}).get("challenge_id"),
                "final_mastery": (b_final.get("state") or {}).get("mastery"),
                "explanation": b_explain,
            },
            "differentiated": differentiated,
            "headline": "Same starting point. Different evidence. Different decision.",
            "label": DEMO_SCENARIO_LABEL,
            "promise": PROMISE_SHORT,
            "same_start": start_challenge,
            "chain": [
                "Same start",
                "Different evidence",
                "Different state",
                "Different strategy",
                "Different challenge",
            ],
            "live_engine": True,
        }

    def reset_session(self, session_id: str | None = None) -> dict[str, Any]:
        """Start a clean session. The previous session is not reused."""
        topic_id = "algebra"
        mode = "learner"
        if session_id:
            meta = self._meta.get(session_id)
            if meta is None:
                try:
                    self.tutor.get_session(session_id)
                except SessionNotFoundError as exc:
                    raise SessionUnavailableError(str(exc)) from exc
                raise SessionUnavailableError(f"unknown session: {session_id}")
            topic_id = meta.topic_id
            if meta.mode == "demo":
                return self.start_demo()
            mode = "learner" if meta.mode == "research" else meta.mode
        return self.create_session(topic_id=topic_id, mode=mode)

    def engine_session(self, session_id: str):
        """Return the AdaptiveTutor session for this product session."""
        session, _meta = self._require(session_id)
        return session

    def engine_decision(self, session_id: str) -> str | None:
        """Expose the latest engine decision for preservation tests. Not used by UI logic."""
        session, _meta = self._require(session_id)
        if not session.traces:
            return None
        return session.traces[-1].decision.value

    def _scripted_run(
        self,
        *,
        topic_id: str,
        learner_id: str,
        kinds: tuple[str, ...],
        initial_challenge: str,
        mode: str,
    ) -> dict[str, Any]:
        view = self.create_session(
            topic_id=topic_id,
            learner_id=learner_id,
            max_steps=max(len(kinds), 1),
            mode=mode,
            initial_challenge=initial_challenge,
        )
        session_id = view["session_id"]
        for index, kind in enumerate(kinds, start=1):
            session, _meta = self._require(session_id)
            challenge = session.current_challenge
            scripted = build_scripted_response(
                challenge,
                kind,
                learner_id=learner_id,
                response_id=f"{session_id}-R-{index:03d}",
            )
            self.submit_response(
                session_id,
                answer=scripted.answer,
                confidence=scripted.learner_confidence.value,
                reasoning=scripted.reasoning,
                challenge_id=challenge.challenge_id,
            )
        return {
            "session": self.get_session(session_id),
            "trace": self.get_trace(session_id),
        }

    def _require(self, session_id: str) -> tuple[Any, ProductSession]:
        meta = self._meta.get(session_id)
        if meta is None:
            try:
                self.tutor.get_session(session_id)
            except SessionNotFoundError as exc:
                raise SessionUnavailableError(str(exc)) from exc
            raise SessionUnavailableError(f"unknown session: {session_id}")
        tutor = self._tutor_for(meta)
        try:
            session = tutor.get_session(session_id)
        except SessionNotFoundError as exc:
            raise SessionUnavailableError(str(exc)) from exc
        return session, meta

    def _session_view(self, session, meta: ProductSession) -> dict[str, Any]:
        complete = session.step_number >= meta.max_steps
        unavailable = session.current_challenge.challenge_id == "UNAVAILABLE"
        last = session.traces[-1] if session.traces else None
        topic = self._resolve_topic(meta.topic_id)[0]
        status = "complete" if complete else "awaiting_answer"
        if unavailable and not complete:
            status = "challenge_unavailable"
        opening = opening_state(
            session.learner_state,
            session.strategy_state,
            concept=topic.name if topic.topic_id != "algebra" else "Basic Algebra",
        )
        if not session.traces:
            opening["mastery"] = "uncertain"
            opening["confidence"] = "low"
            opening["strategy"] = "ASSESS"
            opening["strategy_code"] = "ASSESS"
        payload = {
            "session_id": session.session_id,
            "learner_id": session.learner_id,
            "status": status,
            "mode": meta.mode,
            "topic": topic.to_dict(),
            "opening": opening,
            "current_strategy": session.strategy_state.current_strategy.value,
            "current_strategy_label": strategy_label(session.strategy_state.current_strategy),
            "progress": {
                "current": min(session.step_number + (0 if complete else 1), meta.max_steps),
                "completed": session.step_number,
                "total": meta.max_steps,
            },
            "challenge": None
            if complete
            else public_challenge(session.current_challenge, include_answer=False),
            "understanding": understanding_view(session.learner_state),
            "last_result": None if last is None else self._public_step(last, meta),
            "complete": complete,
            "can_submit": not complete and not unavailable,
            "confidence_scale": scale_options(),
            "evidence_plan": evidence_plan(session, session.current_challenge),
            "subject_id": meta.subject_id,
            "runtime": meta.runtime,
            "reasoning_prompt": "How did you get this?",
            "reasoning_help": (
                "Your reasoning helps ADAPT understand what you know — "
                "not just whether you got the answer right."
            ),
        }
        plan = payload["evidence_plan"]
        payload["reasoning_prompt"] = plan["reasoning_prompt"]
        payload["reasoning_help"] = plan["reasoning_help"]
        payload["note_prompt"] = plan.get("note_prompt") or "Add a note"
        payload["theme"] = subject_theme(meta.subject_id)
        payload["presentation"] = (
            None
            if complete
            else challenge_presentation(
                session.current_challenge.challenge_id,
                subject_id=meta.subject_id,
            )
        )
        payload["concept_id"] = meta.concept_id
        payload["recent_challenge_ids"] = list(session.used_challenge_ids)
        payload["rotation"] = {
            "window": 8,
            "policy": "avoid the same challenge in the recent window unless the bank is exhausted or the strategy is REMEDIATE",
        }
        payload["llm_enabled"] = bool(meta.llm_enabled)
        payload["evidence_source"] = (meta.last_workflow or {}).get("source")
        if meta.llm_enabled:
            source = (meta.last_workflow or {}).get("source")
            payload["evidence_source_label"] = _evidence_source_label(source)
        else:
            payload["evidence_source_label"] = None
        if meta.mode == "demo":
            payload["demo_label"] = DEMO_SCENARIO_LABEL
        return payload

    def _public_step(self, step, meta: ProductSession | None = None) -> dict[str, Any]:
        selection = None if meta is None else meta.last_selection
        workflow = None if meta is None else meta.last_workflow
        source = None if workflow is None else workflow.get("source")
        payload = {
            "step_number": step.step_number,
            "feedback": feedback_from_evidence(step.evidence),
            "adaptation": adaptation_from_step(step),
            "next_challenge": public_challenge(step.next_challenge, include_answer=False),
            "understanding": understanding_view(step.state_after),
            "learned_something": step.step_number == 1,
            "human_explanation": human_trace_explanation(step),
            "noticed": what_adapt_noticed(step),
            "why_this_question": why_this_question(step, selection=selection),
            "explanation": learner_explanation(step),
            "adaptation_view": learner_adaptation_chain(step),
            "evidence_source": source,
        }
        payload["evidence_source_label"] = _evidence_source_label(source)
        return payload

    def _step_result_view(self, session, meta: ProductSession, *, include_research: bool) -> dict[str, Any]:
        view = self._session_view(session, meta)
        last = session.traces[-1]
        view["result"] = self._public_step(last, meta)
        if include_research:
            view["research"] = chain_link(last, include_answers=True)
        view["status"] = "showing_feedback" if not view["complete"] else "complete"
        return view

    def get_progress(self, session_id: str | None = None, *, learner_id: str | None = None) -> dict[str, Any]:
        subject_id = None
        session_completed = 0
        session_concepts: list[str] = []
        if session_id:
            session, meta = self._require(session_id)
            learner_id = learner_id or meta.learner_id or session.learner_id
            subject_id = meta.subject_id
            session_completed = session.step_number
            session_concepts = [session.concept_id]
            self._progress.setdefault(learner_id, {})[session.concept_id] = (
                session.learner_state.mastery_estimate
            )
        mastery = dict(self._progress.get(learner_id or "", {}) or {})
        activity = dict(self._activity.get(learner_id or "", {}) or {})
        if not mastery and session_id:
            session, meta = self._require(session_id)
            mastery = {session.concept_id: session.learner_state.mastery_estimate}
            subject_id = meta.subject_id
        return learner_progress_view(
            concept_mastery=mastery,
            activity=activity,
            subject_id=subject_id,
            session_completed=session_completed,
            session_concepts=session_concepts,
        )

    def get_insights(self, session_id: str) -> dict[str, Any]:
        session, _meta = self._require(session_id)
        return session_insights(session)

    def get_journey(
        self,
        session_id: str | None = None,
        *,
        learner_id: str | None = None,
        subject_id: str | None = None,
    ) -> dict[str, Any]:
        if session_id:
            session, meta = self._require(session_id)
            payload = session_journey(session)
            learner_id = learner_id or meta.learner_id or session.learner_id
            subject_id = subject_id or meta.subject_id
            mastery = dict(self._progress.get(learner_id or "", {}) or {})
            activity = dict(self._activity.get(learner_id or "", {}) or {})
            payload["catalog"] = catalog_journey(
                subject_id=subject_id,
                concept_mastery=mastery,
                activity=activity,
                recommended_id=recommend_concept_id(subject_id, mastery, activity) if subject_id else None,
            )
            return payload
        mastery = dict(self._progress.get(learner_id or "", {}) or {})
        activity = dict(self._activity.get(learner_id or "", {}) or {})
        return catalog_journey(
            subject_id=subject_id,
            concept_mastery=mastery,
            activity=activity,
            recommended_id=recommend_concept_id(subject_id, mastery, activity) if subject_id else None,
        )

    def _trace_view(self, session, meta: ProductSession) -> dict[str, Any]:
        chain = []
        for index, step in enumerate(session.traces):
            link = chain_link(step, include_answers=True)
            if index < len(meta.history):
                workflow = meta.history[index].get("llm_workflow")
                if workflow:
                    link["workflow"] = workflow
                    link["evidence_source"] = workflow.get("source")
                    link["nodes"] = workflow.get("nodes")
            chain.append(link)
        return {
            "session_id": session.session_id,
            "topic_id": meta.topic_id,
            "chain": chain,
            "timeline": timeline_from_session(session),
            "complete_links": sum(1 for item in chain if item["complete"]),
            "total_links": len(chain),
            "current_strategy": session.strategy_state.current_strategy.value,
            "current_strategy_label": strategy_label(session.strategy_state.current_strategy),
            "understanding": understanding_view(session.learner_state),
            "research_state": {
                "mastery": round(session.learner_state.mastery_estimate, 4),
                "confidence": round(session.learner_state.confidence, 4),
                "evidence_strength": session.learner_state.evidence_strength.value,
                "uncertainty": session.learner_state.uncertainty.value,
                "trajectory": session.learner_state.learning_trajectory.value,
                "strategy": session.strategy_state.current_strategy.value,
            },
            "journey": session_journey(session),
            "trace_complete": all(item["complete"] for item in chain) if chain else True,
            "llm_enabled": bool(meta.llm_enabled),
            "workflow": meta.last_workflow,
            "workflow_chain": [
                "Human Input",
                "Gemini Evidence",
                "Validation",
                "Learner State",
                "Strategy",
                "Next Challenge",
            ]
            if meta.llm_enabled
            else ["Evidence", "Learner State", "Strategy", "Next Challenge"],
        }
