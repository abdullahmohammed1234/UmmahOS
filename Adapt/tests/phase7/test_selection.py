from adapt.content.catalog import CATALOG
from adapt.history.memory import ChallengeHistory
from adapt.models.adaptation_decision import AdaptationDecision
from adapt.models.enums import AdaptationAction, DiagnosticConfidence, StrategyName
from adapt.models.learner_state import initial_learner_state
from adapt.selection.selector import Phase7ChallengeSelector


def _decision(action=AdaptationAction.INCREASE_DIFFICULTY):
    return AdaptationDecision(
        decision=action,
        reason=("test_reason",),
        confidence=DiagnosticConfidence.MODERATE,
        evidence_used=("E-1",),
    )


def _state(concept="csafety_coded_recognition"):
    return initial_learner_state("L7", concept)


def test_selector_returns_valid_challenge():
    selector = Phase7ChallengeSelector()
    current = CATALOG.engine_challenge("CSAFE-CTX-001")
    chosen = selector.select(_decision(), _state(), current, ["CSAFE-CTX-001"])
    assert CATALOG.challenge(chosen.challenge_id) is not None


def test_strategy_compatibility_is_respected():
    selector = Phase7ChallengeSelector()
    current = CATALOG.engine_challenge("CSAFE-CTX-001")
    probe = selector.select(
        _decision(AdaptationAction.PROBE_UNCERTAINTY),
        _state(),
        current,
        ["CSAFE-CTX-001"],
        StrategyName.PROBE,
    )
    meta = CATALOG.challenge(probe.challenge_id)
    assert meta.challenge_type in {
        "DIAGNOSTIC",
        "PREDICTION",
        "ERROR_ANALYSIS",
        "COMPARE",
        "EXPLANATION",
        "TRUE_FALSE",
        "CONCEPT_CHECK",
        "REMEDIATION",
        "DEBUG",
        "MATCH",
        "EXPLAIN_CHOICE",
        "DIAGRAM",
        "SHORT_ANSWER",
        "SCENARIO",
        "APPLICATION",
    }


def test_previously_seen_avoided_when_alternatives_exist():
    selector = Phase7ChallengeSelector()
    current = CATALOG.engine_challenge("CSAFE-CTX-001")
    used = ["CSAFE-CTX-001", "CSAFE-CTX-002", "CSAFE-CTX-003"]
    chosen = selector.select(_decision(AdaptationAction.MAINTAIN_DIFFICULTY), _state(), current, used, StrategyName.MAINTAIN)
    assert chosen.challenge_id not in used


def test_repetition_allowed_for_remediation():
    selector = Phase7ChallengeSelector()
    current = CATALOG.engine_challenge("CSAFE-COD-003")
    used = ["CSAFE-COD-003"]
    chosen = selector.select(
        _decision(AdaptationAction.REMEDIATE),
        _state("csafety_neutral_tone"),
        current,
        used,
        StrategyName.REMEDIATE,
    )
    assert chosen.challenge_id
    meta = CATALOG.challenge(chosen.challenge_id)
    assert meta.challenge_type in {"REMEDIATION", "ERROR_ANALYSIS", "COMPARE", "TRUE_FALSE", "DIAGNOSTIC", "SCENARIO"}


def test_family_repetition_is_controlled():
    selector = Phase7ChallengeSelector()
    current = CATALOG.engine_challenge("CSAFE-CTX-001")
    used = ["CSAFE-CTX-001", "CSAFE-CTX-002"]
    chosen = selector.select(_decision(AdaptationAction.MAINTAIN_DIFFICULTY), _state(), current, used, StrategyName.MAINTAIN)
    meta = CATALOG.challenge(chosen.challenge_id)
    if meta.family == "CSAFE-CTX":
        alternatives = [
            item
            for item in CATALOG.challenges
            if item.topic_id == "csafety-context" and item.family != "CSAFE-CTX"
        ]
        assert not alternatives


def test_different_challenge_types_can_be_selected():
    selector = Phase7ChallengeSelector()
    current = CATALOG.engine_challenge("CSAFE-COD-001")
    types = set()
    used = ["CSAFE-COD-001"]
    challenge = current
    for action, strategy in (
        (AdaptationAction.INCREASE_DIFFICULTY, StrategyName.INCREASE),
        (AdaptationAction.PROBE_UNCERTAINTY, StrategyName.PROBE),
        (AdaptationAction.REMEDIATE, StrategyName.REMEDIATE),
        (AdaptationAction.MAINTAIN_DIFFICULTY, StrategyName.MAINTAIN),
    ):
        chosen = selector.select(_decision(action), _state(), challenge, used, strategy)
        types.add(CATALOG.challenge(chosen.challenge_id).challenge_type)
        used.append(chosen.challenge_id)
        challenge = chosen
    assert len(types) >= 2


def test_deterministic_selection_with_identical_inputs():
    a = Phase7ChallengeSelector()
    b = Phase7ChallengeSelector()
    current = CATALOG.engine_challenge("CSAFE-CTX-001")
    used = ["CSAFE-CTX-001"]
    first = a.select(_decision(), _state(), current, used, StrategyName.INCREASE)
    second = b.select(_decision(), _state(), current, list(used), StrategyName.INCREASE)
    assert first.challenge_id == second.challenge_id


def test_selector_does_not_modify_mastery():
    selector = Phase7ChallengeSelector()
    state = _state()
    before = state.mastery_estimate
    selector.select(_decision(), state, CATALOG.engine_challenge("CSAFE-CTX-001"), ["CSAFE-CTX-001"])
    assert state.mastery_estimate == before


def test_history_records_attempts():
    history = ChallengeHistory()
    assert history.recently_seen("X") is False
    from adapt.history.memory import ChallengeAttempt

    history.record(
        ChallengeAttempt("X", "S", 1, "c", 2, "DIRECT", "fam", "correct", "MAINTAIN")
    )
    assert history.recently_seen("X")
    assert history.previously_mastered("X")
