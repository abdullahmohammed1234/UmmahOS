"""Participant records. Raw files are never overwritten."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from adapt.eval.constants import DELAYED_RETENTION_STATUS, HUMAN_SOURCE
from adapt.eval.survey import empty_survey

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RAW_DIR = ROOT / "results" / "phase5" / "raw"


def empty_condition() -> dict[str, Any]:
    return {
        "training_score": None,
        "post_test_score": None,
        "gain": None,
        "strategies": [],
        "training": [],
        "post_test": None,
        "survey": empty_survey(),
        "completed": False,
        "session_ids": [],
        "dropout": False,
    }


def new_record(
    participant_id: str,
    *,
    condition_order: list[str],
    source: str = HUMAN_SOURCE,
) -> dict[str, Any]:
    return {
        "participant_id": participant_id,
        "source": source,
        "condition_order": list(condition_order),
        "pre_test": None,
        "adapt": empty_condition(),
        "baseline": empty_condition(),
        "misconception_recovery": {"adapt": None, "baseline": None},
        "delayed_retention": DELAYED_RETENTION_STATUS,
        "excluded": False,
        "exclusion_reason": None,
    }


def raw_path(participant_id: str, raw_dir: Path | None = None) -> Path:
    directory = raw_dir or DEFAULT_RAW_DIR
    return directory / f"{participant_id}.json"


def save_raw_record(
    record: dict[str, Any],
    *,
    raw_dir: Path | None = None,
    overwrite: bool = False,
) -> Path:
    directory = raw_dir or DEFAULT_RAW_DIR
    directory.mkdir(parents=True, exist_ok=True)
    path = raw_path(record["participant_id"], directory)
    if path.exists() and not overwrite:
        raise FileExistsError(
            f"raw record already exists: {path}. "
            "Do not overwrite. Write a corrected copy instead."
        )
    path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
    return path


def load_raw_record(participant_id: str, raw_dir: Path | None = None) -> dict[str, Any]:
    path = raw_path(participant_id, raw_dir)
    return json.loads(path.read_text(encoding="utf-8"))


def list_human_records(raw_dir: Path | None = None) -> list[dict[str, Any]]:
    directory = raw_dir or DEFAULT_RAW_DIR
    if not directory.exists():
        return []
    records = []
    for path in sorted(directory.glob("P*.json")):
        if path.name.endswith(".corrected.json"):
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("source") == HUMAN_SOURCE and not data.get("excluded"):
            records.append(data)
    return records


def list_synthetic_records(raw_dir: Path | None = None) -> list[dict[str, Any]]:
    directory = raw_dir or DEFAULT_RAW_DIR
    if not directory.exists():
        return []
    records = []
    for path in sorted(directory.glob("SYN-*.json")):
        records.append(json.loads(path.read_text(encoding="utf-8")))
    return records
