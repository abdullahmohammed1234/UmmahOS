"""M9-011 — Same seed/input remains reproducible."""

from tests.phase4.helpers import make_service

SEED = 20260815


def test_m9_011_determinism():
    a = make_service(seed=SEED)
    b = make_service(seed=SEED)
    cf_a = a.run_counterfactual()
    cf_b = b.run_counterfactual()
    assert cf_a["learner_a"]["final_decision"] == cf_b["learner_a"]["final_decision"]
    assert cf_a["learner_b"]["final_decision"] == cf_b["learner_b"]["final_decision"]
    sa = a.create_session(concept_id="csafety_context_preservation", session_id="P9-DET-A", max_steps=1)
    sb = b.create_session(concept_id="csafety_context_preservation", session_id="P9-DET-B", max_steps=1)
    assert sa["challenge"]["challenge_id"] == sb["challenge"]["challenge_id"]
