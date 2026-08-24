"""Seven-step ADAPT interaction pipeline.

Phase 1 path (default): analyzer → updater → AdaptationEngine → selector.
Phase 2 path: analyzer → updater → StrategyState → AdaptiveStrategyEngine → selector.
The Phase 1 engine remains the default so frozen 1E/1F experiments are unchanged.
"""

from __future__ import annotations

from adapt.adaptation.adaptation_engine import AdaptationEngine
from adapt.adaptation.challenge_selector import ChallengeSelector
from adapt.analysis.evidence_analyzer import EvidenceAnalyzer
from adapt.errors import MissingChallengeError
from adapt.models.challenge import Challenge
from adapt.models.evidence import Evidence
from adapt.models.learner_response import LearnerResponse
from adapt.models.learner_state import LearnerState
from adapt.models.strategy import StrategyState
from adapt.state.state_updater import StateUpdater
from adapt.strategy.engine import AdaptiveStrategyEngine
from adapt.trace.decision_trace import DecisionTrace


class AdaptPipeline:
    def __init__(
        self,
        analyzer: EvidenceAnalyzer | None = None,
        updater: StateUpdater | None = None,
        engine: AdaptationEngine | None = None,
        selector: ChallengeSelector | None = None,
        strategy_engine: AdaptiveStrategyEngine | None = None,
    ) -> None:
        self.analyzer = analyzer or EvidenceAnalyzer()
        self.updater = updater or StateUpdater()
        self.engine = engine or AdaptationEngine()
        self.selector = selector or ChallengeSelector()
        self.strategy_engine = strategy_engine

    def run(
        self,
        *,
        learner_state: LearnerState,
        challenge: Challenge | None,
        response: LearnerResponse,
        history: list[LearnerResponse] | None = None,
        recent_evidence: list[Evidence] | None = None,
        used_challenge_ids: list[str] | None = None,
        interaction_id: str | None = None,
        strategy_state: StrategyState | None = None,
    ) -> DecisionTrace:
        if challenge is None:
            raise MissingChallengeError("ADAPT interaction requires a challenge")

        evidence = self.analyzer.analyze(response, challenge, history)
        updated = self.updater.update(learner_state, evidence)
        strategy_decision = None
        next_strategy = None
        if self.strategy_engine is not None:
            strategy_decision = self.strategy_engine.decide(
                learner_state=updated,
                evidence=evidence,
                history=history,
                current_strategy=strategy_state,
                recent_evidence=recent_evidence,
            )
            decision = strategy_decision.to_adaptation_decision()
            next_strategy = strategy_decision.strategy_state
        else:
            decision = self.engine.decide(
                updated, challenge, evidence, recent_evidence=recent_evidence
            )
        next_challenge = self.selector.select(
            decision,
            updated,
            challenge,
            used_challenge_ids=used_challenge_ids,
        )
        n = len(updated.recent_performance.outcomes)
        resolved_id = interaction_id or f"I-{n:03d}"
        return DecisionTrace(
            interaction_id=resolved_id,
            learner_state_before=learner_state,
            challenge=challenge,
            learner_response=response,
            evidence=evidence,
            learner_state_after=updated,
            adaptation_decision=decision,
            next_challenge=next_challenge,
            strategy_state=next_strategy,
            strategy_decision=strategy_decision,
            strategy_transition=None if strategy_decision is None else strategy_decision.transition,
        )

    def run_sequence(
        self,
        *,
        learner_state: LearnerState,
        steps: list[tuple[Challenge, LearnerResponse]],
        strategy_state: StrategyState | None = None,
    ) -> list[DecisionTrace]:
        traces: list[DecisionTrace] = []
        state = learner_state
        history: list[LearnerResponse] = []
        recent_evidence: list[Evidence] = []
        used = [challenge.challenge_id for challenge, _ in steps[:1]]
        current_strategy = strategy_state
        for challenge, response in steps:
            trace = self.run(
                learner_state=state,
                challenge=challenge,
                response=response,
                history=list(history),
                recent_evidence=list(recent_evidence),
                used_challenge_ids=list(used),
                strategy_state=current_strategy,
            )
            traces.append(trace)
            state = trace.learner_state_after
            current_strategy = trace.strategy_state
            history.append(response)
            recent_evidence.append(trace.evidence)
            used.append(trace.next_challenge.challenge_id)
        return traces
