"""Capture Phase 10 frontend screenshots. Requires Playwright and both servers.

If Playwright is unavailable, the caller should record NOT CAPTURED.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "phase10" / "screenshots"


def main() -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("NOT EXECUTED: Playwright is not installed.")
        return 2

    base = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:3000"
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        page.goto(base + "/", wait_until="networkidle")
        page.wait_for_timeout(500)
        page.screenshot(path=str(OUT / "01-landing.png"), full_page=True)

        page.goto(base + "/subjects", wait_until="networkidle")
        page.wait_for_timeout(400)
        page.screenshot(path=str(OUT / "02-subjects.png"), full_page=True)

        page.goto(base + "/subjects/quantum", wait_until="networkidle")
        page.wait_for_timeout(800)
        page.screenshot(path=str(OUT / "03-concept.png"), full_page=True)
        page.screenshot(path=str(OUT / "10-quantum.png"), full_page=True)

        page.get_by_role("button").filter(has=page.get_by_role("heading", name="Superposition")).click()
        page.wait_for_url("**/learn**", timeout=15000)
        page.wait_for_timeout(500)
        page.screenshot(path=str(OUT / "04-challenge.png"), full_page=True)

        answer_labels = page.locator("label:has(input[name='answer'])")
        if answer_labels.count():
            answer_labels.first.click()
        elif page.locator("#answer").count():
            page.fill("#answer", "False")
        page.locator("label:has(input[name='confidence'][value='5'])").click()
        page.locator("label:has(input[name='approach'][value='knew'])").click()
        page.get_by_role("button", name="Continue").click()
        page.wait_for_selector("[data-screen='feedback']")
        page.wait_for_timeout(400)
        page.screenshot(path=str(OUT / "05-feedback.png"), full_page=True)
        page.screenshot(path=str(OUT / "06-adaptation.png"), full_page=True)

        session = ""
        if "session=" in page.url:
            session = page.url.split("session=", 1)[-1].split("&", 1)[0]
        page.goto(base + (f"/progress?session={session}" if session else "/progress"), wait_until="networkidle")
        page.screenshot(path=str(OUT / "07-progress.png"), full_page=True)
        page.goto(base + "/research", wait_until="networkidle")
        page.screenshot(path=str(OUT / "08-research.png"), full_page=True)
        page.goto(base + "/counterfactual", wait_until="networkidle")
        page.wait_for_timeout(1200)
        page.screenshot(path=str(OUT / "09-counterfactual.png"), full_page=True)
        browser.close()
    print(f"Wrote screenshots to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
