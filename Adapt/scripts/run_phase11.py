"""Run the UmmahOS ADAPT API on port 8765."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run ADAPT API for UmmahOS")
    args = parser.parse_args()
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
    print("API: http://127.0.0.1:8765")
    return subprocess.call([sys.executable, "-m", "app"], cwd=ROOT, env=env)


if __name__ == "__main__":
    raise SystemExit(main())
