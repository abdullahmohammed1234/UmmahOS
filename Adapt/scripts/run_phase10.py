"""Run the Phase 10 stack: Python API on 8765, Next.js on 3000."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run ADAPT Phase 10 frontend + API")
    parser.add_argument("--api-only", action="store_true")
    args = parser.parse_args()
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
    api = subprocess.Popen([sys.executable, "-m", "app"], cwd=ROOT, env=env)
    if args.api_only:
        return api.wait()
    npm = shutil.which("npm")
    if npm is None:
        print("npm was not found. The API is running at http://127.0.0.1:8765")
        return api.wait()
    try:
        print("API: http://127.0.0.1:8765")
        print("Frontend: http://127.0.0.1:3000")
        return subprocess.call([npm, "run", "dev"], cwd=FRONTEND)
    finally:
        api.terminate()


if __name__ == "__main__":
    raise SystemExit(main())
