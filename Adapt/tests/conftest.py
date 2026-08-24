"""Phase 1D test reporting: totals plus a separately identifiable counterfactual result."""

from __future__ import annotations

import sys
from pathlib import Path

# `python -m pytest` puts the repo root on sys.path[0], so the launcher package
# `app/` shadows `src/app`. Prefer src so Phase 4 `from app.server` resolves.
_SRC = str(Path(__file__).resolve().parents[1] / "src")
if _SRC in sys.path:
    sys.path.remove(_SRC)
sys.path.insert(0, _SRC)
for _name in [key for key in list(sys.modules) if key == "app" or key.startswith("app.")]:
    del sys.modules[_name]


def pytest_terminal_summary(terminalreporter, exitstatus, config) -> None:
    stats = terminalreporter.stats
    passed = len(stats.get("passed", []))
    failed = len(stats.get("failed", []))
    skipped = len(stats.get("skipped", []))
    errors = len(stats.get("error", []))
    total = passed + failed + skipped + errors

    counterfactual_failed = False
    counterfactual_seen = False
    for reports in stats.values():
        for report in reports:
            nodeid = getattr(report, "nodeid", "")
            if "counterfactual" in nodeid:
                counterfactual_seen = True
                if getattr(report, "outcome", "") == "failed":
                    counterfactual_failed = True

    core_failed = failed > 0 or errors > 0
    terminalreporter.write_sep("=", "Phase 1D Summary")
    terminalreporter.write_line(f"Total tests: {total}")
    terminalreporter.write_line(f"Passed: {passed}")
    terminalreporter.write_line(f"Failed: {failed}")
    terminalreporter.write_line(f"Skipped: {skipped}")
    terminalreporter.write_line(f"CORE TESTS: {'FAIL' if core_failed else 'PASS'}")
    if not counterfactual_seen:
        cf_status = "MISSING"
    elif counterfactual_failed:
        cf_status = "FAIL"
    else:
        cf_status = "PASS"
    terminalreporter.write_line(f"COUNTERFACTUAL ADAPTATION TEST: {cf_status}")
