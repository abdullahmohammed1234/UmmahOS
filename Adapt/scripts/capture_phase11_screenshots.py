"""Capture Phase 11 frontend screenshots. Requires Playwright and both servers.

If Playwright is unavailable, the caller should record NOT CAPTURED.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "phase11" / "screenshots"


def _goto(page, url: str) -> None:
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(800)


def main() -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("NOT EXECUTED: Playwright is not installed.")
        return 2

    base = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:3000"
    OUT.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        page.on("pageerror", lambda err: errors.append(str(err)))

        _goto(page, base + "/")
        page.wait_for_selector("h1")
        page.screenshot(path=str(OUT / "01-landing.png"), full_page=True)

        _goto(page, base + "/subjects")
        page.wait_for_selector("h1")
        page.screenshot(path=str(OUT / "02-subjects.png"), full_page=True)

        _goto(page, base + "/subjects/quantum")
        page.wait_for_selector("text=Superposition", timeout=20000)
        page.wait_for_timeout(700)
        page.screenshot(path=str(OUT / "08-quantum.png"), full_page=True)

        page.get_by_role("heading", name="Superposition").first.click()
        page.wait_for_url("**/learn**", timeout=20000)
        page.wait_for_selector("[data-screen='challenge']")
        page.wait_for_timeout(400)
        page.screenshot(path=str(OUT / "03-challenge.png"), full_page=True)

        answer_labels = page.locator("label:has(input[name='answer'])")
        if answer_labels.count():
            answer_labels.first.click()
        elif page.locator("#answer").count():
            page.fill("#answer", "False")
        page.locator("label:has(input[name='confidence'][value='5'])").click()
        page.locator("label:has(input[name='approach'][value='knew'])").click()
        page.get_by_role("button", name="Continue").click()
        page.wait_for_selector("[data-screen='feedback']")
        page.wait_for_timeout(500)
        page.locator("[data-screen='noticed']").screenshot(path=str(OUT / "04-noticed.png"))
        page.locator("[data-adaptation-moment]").screenshot(path=str(OUT / "05-adaptation.png"))

        _goto(page, base + "/research")
        page.wait_for_selector("h1")
        page.screenshot(path=str(OUT / "06-research.png"), full_page=True)
        _goto(page, base + "/counterfactual")
        page.wait_for_selector("text=Engine decision", timeout=25000)
        page.wait_for_timeout(400)
        page.screenshot(path=str(OUT / "07-counterfactual.png"), full_page=True)

        mobile = browser.new_page(viewport={"width": 360, "height": 740})
        _goto(mobile, base + "/")
        mobile.wait_for_selector("h1")
        mobile.screenshot(path=str(OUT / "09-mobile-landing.png"), full_page=True)
        browser.close()

    log = OUT / "console-errors.txt"
    log.write_text("\n".join(errors) if errors else "none\n", encoding="utf-8")
    print(f"Wrote screenshots to {OUT}")
    if errors:
        print("PAGE ERRORS:")
        print("\n".join(errors))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
