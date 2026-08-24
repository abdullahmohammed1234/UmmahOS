"""Phase 1D test entry point with core + counterfactual reporting."""

from __future__ import annotations

import subprocess
import sys


def main() -> int:
    print("=== ADAPT Phase 1D: full suite ===")
    full = subprocess.call([sys.executable, "-m", "pytest"])
    print("\n=== ADAPT Phase 1D: counterfactual test only ===")
    counterfactual = subprocess.call(
        [sys.executable, "-m", "pytest", "tests/test_counterfactual_adaptation.py"]
    )
    if full != 0 or counterfactual != 0:
        print("\nPhase 1D: FAIL")
        return 1
    print("\nPhase 1D: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
