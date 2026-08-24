"""Integrity helpers: baseline must not call AdaptiveTutor; ADAPT must."""

from __future__ import annotations

import ast
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parent
FORBIDDEN_BASELINE_IMPORTS = {
    "AdaptiveTutor",
    "ProductService",
    "AdaptiveStrategyEngine",
    "StateUpdater",
    "AdaptPipeline",
    "AdaptationEngine",
}


def baseline_forbidden_imports(source: str | None = None) -> list[str]:
    text = source
    if text is None:
        text = (EVAL_DIR / "baseline.py").read_text(encoding="utf-8")
    tree = ast.parse(text)
    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name.split(".")[-1]
                if name in FORBIDDEN_BASELINE_IMPORTS or "tutor.tutor" in alias.name:
                    found.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                combined = f"{module}.{alias.name}"
                if alias.name in FORBIDDEN_BASELINE_IMPORTS or "AdaptiveTutor" in combined:
                    found.append(combined)
                if module.endswith("tutor.tutor") or module.endswith("product.service"):
                    found.append(combined)
    return found
