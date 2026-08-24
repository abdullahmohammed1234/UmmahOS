"""Synthetic analysis cases. Never present these as human results."""

from __future__ import annotations

from adapt.eval.constants import SYNTHETIC_SOURCE
from adapt.eval.protocol import assign_condition_order
from adapt.eval.records import new_record
from adapt.eval.scoring import learning_gain


def _gains(participant_id: str, adapt_gain: float, baseline_gain: float, pre: float = 0.50) -> dict:
    record = new_record(
        participant_id,
        condition_order=assign_condition_order(participant_id),
        source=SYNTHETIC_SOURCE,
    )
    record["pre_test"] = {"score": pre, "n_items": 8, "synthetic": True}
    record["adapt"]["post_test_score"] = pre + adapt_gain
    record["adapt"]["gain"] = learning_gain(pre, pre + adapt_gain)
    record["adapt"]["training_score"] = 0.5
    record["adapt"]["completed"] = True
    record["adapt"]["strategies"] = ["ASSESS", "GATHER_EVIDENCE", "INCREASE"]
    record["baseline"]["post_test_score"] = pre + baseline_gain
    record["baseline"]["gain"] = learning_gain(pre, pre + baseline_gain)
    record["baseline"]["training_score"] = 0.5
    record["baseline"]["completed"] = True
    record["note"] = "SYNTHETIC VALIDATION — not a human participant"
    return record


SYNTHETIC_CASES = (
    {
        "id": "SYN-A",
        "record": _gains("SYN-A", 0.20, 0.10),
        "expected_delta": 0.10,
        "label": "ADAPT gain 0.20, baseline gain 0.10",
    },
    {
        "id": "SYN-B",
        "record": _gains("SYN-B", 0.10, 0.20),
        "expected_delta": -0.10,
        "label": "ADAPT gain 0.10, baseline gain 0.20",
    },
    {
        "id": "SYN-C",
        "record": _gains("SYN-C", 0.15, 0.15),
        "expected_delta": 0.0,
        "label": "equal gain 0.15",
    },
)


def synthetic_records() -> list[dict]:
    return [item["record"] for item in SYNTHETIC_CASES]
