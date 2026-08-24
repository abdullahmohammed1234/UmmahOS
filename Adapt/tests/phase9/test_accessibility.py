"""M9-013 / M9-014 — Responsive and accessibility structure."""

from pathlib import Path

STATIC = Path(__file__).resolve().parents[2] / "src" / "app" / "static"


def test_m9_013_responsive_structure():
    css = (STATIC / "css" / "styles.css").read_text(encoding="utf-8")
    components = (STATIC / "css" / "components.css").read_text(encoding="utf-8")
    app_js = (STATIC / "js" / "app.js").read_text(encoding="utf-8")
    blob = css + components
    for width in ("360px", "768px", "1280px"):
        assert width in blob
    for screen in ("landing", "subjects", "concepts", "challenge", "feedback"):
        assert f'data-screen="{screen}"' in app_js
    assert "Check Answer" in app_js
    assert "subject-grid" in components


def test_m9_014_accessibility_structure():
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    css = (STATIC / "css" / "styles.css").read_text(encoding="utf-8")
    app_js = (STATIC / "js" / "app.js").read_text(encoding="utf-8")
    blob = html + css + app_js
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
    assert "increaseDifficulty" not in blob
    assert "if (correct)" not in app_js
