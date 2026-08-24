"""Re-export src/app/server when the repo-root `app` launcher is imported first.

`python -m pytest` places the repository root on sys.path[0], which shadows
`src/app`. This shim does not implement adaptive behavior.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

_PATH = Path(__file__).resolve().parent.parent / "src" / "app" / "server.py"
_SPEC = importlib.util.spec_from_file_location("_adapt_src_app_server", _PATH)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"cannot load application server from {_PATH}")
_MOD = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MOD)

AdaptHandler = _MOD.AdaptHandler
DEFAULT_HOST = _MOD.DEFAULT_HOST
DEFAULT_PORT = _MOD.DEFAULT_PORT
ProductServer = _MOD.ProductServer
create_server = _MOD.create_server
serve = _MOD.serve
