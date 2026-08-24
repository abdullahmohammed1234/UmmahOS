"""python -m app"""

from __future__ import annotations

import argparse

from app.server import DEFAULT_HOST, DEFAULT_PORT, serve


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the ADAPT learner product")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()
    serve(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
