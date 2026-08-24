"""Accessibility contracts for the Phase 8 product UI."""

from pathlib import Path

STATIC = Path(__file__).resolve().parents[2] / "src" / "app" / "static"


def test_accessibility_contracts():
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    css = (STATIC / "css" / "styles.css").read_text(encoding="utf-8")
    components = (STATIC / "css" / "components.css").read_text(encoding="utf-8")
    app_js = (STATIC / "js" / "app.js").read_text(encoding="utf-8")
    blob = html + css + components + app_js
    assert 'lang="en"' in html
    assert "skip-link" in html
    assert 'href="#main"' in html
    assert ":focus-visible" in css
    assert "prefers-reduced-motion" in css
    assert 'role="radiogroup"' in app_js
    assert "How confident are you?" in app_js
    assert "aria-live" in app_js
    assert "aria-label" in app_js
    assert "aria-current" in app_js
    assert "nav-toggle" in css
    assert "minmax" in components
    assert "increaseDifficulty" not in blob
    assert "if (correct)" not in app_js
