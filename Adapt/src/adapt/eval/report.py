"""Render Phase 5 reports from collected records. Does not invent participants."""

from __future__ import annotations

from typing import Any


def _fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return "NOT COLLECTED"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def metric_markdown_table(rows: list[dict[str, Any]]) -> str:
    lines = [
        "| Metric | ADAPT | Baseline | Difference |",
        "|---|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['metric']} | {_fmt(row['adapt'])} | {_fmt(row['baseline'])} | {_fmt(row['difference'])} |"
        )
    return "\n".join(lines)


def trajectory_table(records: list[dict[str, Any]]) -> str:
    lines = [
        "| Participant | Condition | Pre | Post | Gain |",
        "|---|---|---:|---:|---:|",
    ]
    if not records:
        lines.append("| — | — | NOT COLLECTED | NOT COLLECTED | NOT COLLECTED |")
        return "\n".join(lines)
    for record in records:
        pre = (record.get("pre_test") or {}).get("score")
        for condition in ("ADAPT", "BASELINE"):
            block = record.get(condition.lower()) or {}
            lines.append(
                f"| {record.get('participant_id')} | {condition} | "
                f"{_fmt(pre)} | {_fmt(block.get('post_test_score'))} | {_fmt(block.get('gain'))} |"
            )
    return "\n".join(lines)


def render_report(
    *,
    human: dict[str, Any],
    synthetic: dict[str, Any],
    human_records: list[dict[str, Any]],
    planned: int,
    actual: int,
    reason: str,
) -> str:
    interpretation = human.get("interpretation") or {}
    lines = [
        "# Phase 5 — Learner Evaluation Results",
        "",
        "## Engineering evidence versus human learning evidence",
        "",
        "This file reports two separate kinds of evidence.",
        "",
        "1. **Engineering evidence** — synthetic analysis validation and product-integrity checks.",
        "2. **Human learning evidence** — only records with `source: human`.",
        "",
        "Synthetic cases are never human results.",
        "",
        "## Participants",
        "",
        f"- Planned: {planned}",
        f"- Actual human participants: {actual}",
        f"- Reason: {reason}",
        "",
        "## Human comparison",
        "",
        metric_markdown_table(human.get("table") or []),
        "",
        "## Individual trajectories",
        "",
        trajectory_table(human_records),
        "",
        "## Interpretation (human data)",
        "",
        f"- H1: **{interpretation.get('h1', 'INCONCLUSIVE')}**",
        f"- Reason: {interpretation.get('reason', 'No human data.')}",
        f"- Exploratory: {interpretation.get('exploratory', True)}",
        "",
        "## Delayed retention",
        "",
        "NOT COLLECTED",
        "",
        "## Synthetic analysis validation",
        "",
        "These cases test the analysis implementation only.",
        "",
    ]
    for case in synthetic.get("cases") or []:
        flag = "PASS" if case.get("passed") else "FAIL"
        lines.append(
            f"- `{case['id']}` {flag}: expected delta {case.get('expected_delta')}, "
            f"observed {case.get('observed_delta')} — {case.get('label')}"
        )
    lines.extend(["", "## Failures", "", human.get("failures") or "None recorded.", ""])
    return "\n".join(lines) + "\n"


def simple_svg_bars(title: str, series: list[tuple[str, float]], *, note: str) -> str:
    width = 480
    height = 220
    bars = max(len(series), 1)
    gap = 20
    bar_w = max(20, int((width - 80) / bars) - gap)
    max_val = max((abs(value) for _, value in series), default=1.0) or 1.0
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        f'<rect width="100%" height="100%" fill="#f7f7f4"/>',
        f'<text x="16" y="24" font-family="sans-serif" font-size="14">{title}</text>',
        f'<text x="16" y="{height - 12}" font-family="sans-serif" font-size="10" fill="#666">{note}</text>',
    ]
    axis_y = 160
    for index, (label, value) in enumerate(series):
        x = 40 + index * (bar_w + gap)
        mag = int((abs(value) / max_val) * 90)
        y = axis_y - mag if value >= 0 else axis_y
        color = "#2a6" if value >= 0 else "#c44"
        parts.append(f'<rect x="{x}" y="{y}" width="{bar_w}" height="{max(mag, 1)}" fill="{color}"/>')
        parts.append(
            f'<text x="{x}" y="{axis_y + 16}" font-family="sans-serif" font-size="10">{label}</text>'
        )
    parts.append("</svg>")
    return "\n".join(parts)
