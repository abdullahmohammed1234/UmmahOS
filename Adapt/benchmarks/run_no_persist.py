"""Re-run historical benchmarks without rewriting result files.

python -m benchmarks.run_no_persist
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
for path in (str(SRC), str(ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)

from benchmarks.phase1e.runner import print_summary as print_1e
from benchmarks.phase1e.runner import run_benchmark as run_1e
from benchmarks.phase1f.runner import print_summary as print_1f
from benchmarks.phase1f.runner import run_benchmark as run_1f
from benchmarks.phase2.runner import print_summary as print_2
from benchmarks.phase2.runner import run_benchmark as run_2
from benchmarks.phase3.runner import run_benchmark as run_3
from benchmarks.phase4.runner import run_benchmark as run_4
from benchmarks.phase5.runner import run_benchmark as run_5
from benchmarks.phase7.runner import print_summary as print_7
from benchmarks.phase7.runner import run_benchmark as run_7


def main() -> int:
    print("=== Phase 1E persist=False ===")
    one_e = run_1e(persist=False)
    print_1e(one_e)

    print("=== Phase 1F persist=False ===")
    one_f = run_1f(persist=False)
    print_1f(one_f)

    print("=== Phase 2 persist=False ===")
    two = run_2(persist=False)
    print_2(two)

    print("=== Phase 3 persist=False ===")
    three = run_3(persist=False, seed=20260814)
    print(three["metrics"]["M3-001_end_to_end_adaptation"]["display"])
    print(three["metrics"]["M3-002_state_to_strategy_causality"]["display"])
    print(three["metrics"]["M3-003_strategy_to_challenge_consistency"]["display"])

    print("=== Phase 4 persist=False ===")
    four = run_4(persist=False, seed=20260814)
    print(four["metrics"]["M4-001_task_completion"]["display"])
    print(four["metrics"]["M4-002_adaptive_result_preservation"]["display"])
    print(four["metrics"]["M4-003_trace_visibility"]["display"])

    print("=== Phase 5 persist=False ===")
    five = run_5(persist=False)
    human = five.get("metrics", {}).get("human") or five.get("human") or {}
    print("human n=", five.get("meta", {}).get("actual_human_participants"))
    print("H1", (human.get("interpretation") or {}).get("h1"))
    print("failures", five.get("failures"))
    print("=== Phase 7 persist=False ===")
    seven = run_7(persist=False)
    print_7(seven)
    print("=== Phase 8 persist=False ===")
    from benchmarks.phase8.runner import print_summary as print_8
    from benchmarks.phase8.runner import run_benchmark as run_8

    eight = run_8(persist=False)
    print_8(eight)
    print("=== Phase 9 persist=False ===")
    from benchmarks.phase9.runner import print_summary as print_9
    from benchmarks.phase9.runner import run_benchmark as run_9

    nine = run_9(persist=False)
    print_9(nine)
    print("=== Phase 12 persist=False ===")
    from benchmarks.phase12.runner import print_summary as print_12
    from benchmarks.phase12.runner import run_benchmark as run_12

    twelve = run_12(persist=False)
    print_12(twelve)
    return (
        1
        if five.get("failures")
        or seven.get("failures")
        or eight.get("failures")
        or nine.get("failures")
        else 0
    )


if __name__ == "__main__":
    raise SystemExit(main())
