"""python -m app  (from the repository root)"""

from __future__ import annotations

import sys
from pathlib import Path


def _load_src_app_main():
    root = Path(__file__).resolve().parents[1]
    src = str(root / "src")
    if src in sys.path:
        sys.path.remove(src)
    sys.path.insert(0, src)
    for name in [key for key in sys.modules if key == "app" or key.startswith("app.")]:
        del sys.modules[name]
    from app.__main__ import main  # real module: src/app/__main__.py

    return main


if __name__ == "__main__":
    _load_src_app_main()()
