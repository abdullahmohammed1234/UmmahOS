"""Repo-root launcher so `python -m app` works without installing the package.

The real application lives in `src/app/`. This shim only puts `src/` on
sys.path, then hands off to that package.
"""
