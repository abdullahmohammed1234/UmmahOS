"""Phase 1E counterfactual pair tests."""

from __future__ import annotations

import pytest

from benchmarks.phase1e.evaluator import pair_counterfactuals, run_adapt, run_baseline
from benchmarks.phase1e.scenarios import counterfactual_pairs

pytestmark = pytest.mark.counterfactual


def test_all_three_counterfactual_dimensions_change_adapt_decisions():
    pairs = counterfactual_pairs()
    seen = set()
    for pair_id, members in pairs.items():
        rec_a = run_adapt(members["A"])
        rec_b = run_adapt(members["B"])
        assert rec_a["decision"] != rec_b["decision"], (
            f"{pair_id} ADAPT decisions were identical: {rec_a['decision']}"
        )
        seen.add(members["A"].counterfactual_dimension)
    assert seen == {"reasoning_quality", "misconception", "learner_confidence"}


def test_counterfactual_difference_tracks_changed_dimension():
    pairs = counterfactual_pairs()
    for members in pairs.values():
        dimension = members["A"].counterfactual_dimension
        rec_a = run_adapt(members["A"])
        rec_b = run_adapt(members["B"])
        if dimension == "reasoning_quality":
            assert rec_a["evidence"]["reasoning_quality"] != rec_b["evidence"]["reasoning_quality"]
        elif dimension == "misconception":
            a_misc = rec_a["learner_state_after"]["misconceptions"]
            b_misc = rec_b["learner_state_after"]["misconceptions"]
            assert a_misc != b_misc
        elif dimension == "learner_confidence":
            assert rec_a["evidence"]["confidence_signal"] != rec_b["evidence"]["confidence_signal"]


def test_counterfactual_pair_helper_marks_differentiation():
    pairs = counterfactual_pairs()
    records = []
    for members in pairs.values():
        records.append(run_adapt(members["A"]))
        records.append(run_adapt(members["B"]))
    summarized = pair_counterfactuals(records)
    assert summarized
    assert all(item["expected_different"] for item in summarized)


def test_baseline_is_also_scored_on_counterfactuals():
    members = next(iter(counterfactual_pairs().values()))
    rec_a = run_baseline(members["A"])
    rec_b = run_baseline(members["B"])
    assert rec_a["system"] == rec_b["system"] == "BASELINE"
    assert rec_a["scenario_id"] != rec_b["scenario_id"]
