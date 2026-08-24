"""Capture Phase 9 product screenshots via a live local server."""

from __future__ import annotations

import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from app.server import create_server

OUT = ROOT / "results" / "phase9" / "screenshots"


def main() -> int:
    from playwright.sync_api import sync_playwright

    OUT.mkdir(parents=True, exist_ok=True)
    server = create_server(host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port = server.server_address[1]
    base = f"http://127.0.0.1:{port}"
    time.sleep(0.3)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1280, "height": 800})
            page.goto(base + "/", wait_until="networkidle")
            page.wait_for_selector("h1")
            page.wait_for_timeout(400)
            page.screenshot(path=str(OUT / "01-landing.png"), full_page=True)

            page.click("text=Start Learning")
            page.wait_for_selector(".subject-card")
            page.wait_for_timeout(300)
            page.screenshot(path=str(OUT / "02-subjects.png"), full_page=True)

            page.click("text=Quantum")
            page.wait_for_selector(".concept-card")
            page.wait_for_timeout(300)
            page.screenshot(path=str(OUT / "03-concept.png"), full_page=True)

            page.click("text=Superposition")
            page.wait_for_selector("#challenge-form")
            page.wait_for_timeout(300)
            page.screenshot(path=str(OUT / "04-challenge.png"), full_page=True)

            if page.locator("input[name='answer'][type='radio']").count():
                page.locator("input[name='answer'][type='radio']").first.check()
            elif page.locator("#answer").count():
                page.fill("#answer", "False")
            page.locator("input[name='confidence']").last.check()
            if page.locator("input[name='approach']").count():
                page.locator("input[name='approach']").first.check()
            page.click("text=Check Answer")
            page.wait_for_selector("[data-screen='feedback']")
            page.wait_for_timeout(400)
            page.screenshot(path=str(OUT / "05-feedback.png"), full_page=True)
            page.screenshot(path=str(OUT / "06-adaptation.png"), full_page=True)

            page.click("text=Progress")
            page.wait_for_selector("h1")
            page.wait_for_timeout(300)
            page.screenshot(path=str(OUT / "07-progress.png"), full_page=True)

            page.goto(base + "/", wait_until="networkidle")
            page.click("text=Start Learning")
            page.wait_for_selector(".subject-card")
            page.click("text=Quantum")
            page.wait_for_selector(".concept-card")
            page.click("text=Superposition")
            page.wait_for_selector("#challenge-form")
            if page.locator("input[name='answer'][type='radio']").count():
                page.locator("input[name='answer'][type='radio']").first.check()
            page.locator("input[name='confidence']").last.check()
            page.click("text=Check Answer")
            page.wait_for_selector("[data-screen='feedback']")
            page.click("text=Research mode")
            page.wait_for_selector(".research-panel")
            page.wait_for_timeout(300)
            page.screenshot(path=str(OUT / "08-research.png"), full_page=True)

            page.goto(base + "/#counterfactual", wait_until="networkidle")
            page.wait_for_selector("h1")
            page.wait_for_timeout(800)
            page.screenshot(path=str(OUT / "09-counterfactual.png"), full_page=True)

            mobile = browser.new_page(viewport={"width": 360, "height": 740})
            mobile.goto(base + "/", wait_until="networkidle")
            mobile.wait_for_selector("h1")
            mobile.wait_for_timeout(400)
            mobile.screenshot(path=str(OUT / "10-mobile.png"), full_page=True)
            mobile.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    names = [
        "01-landing.png",
        "02-subjects.png",
        "03-concept.png",
        "04-challenge.png",
        "05-feedback.png",
        "06-adaptation.png",
        "07-progress.png",
        "08-research.png",
        "09-counterfactual.png",
        "10-mobile.png",
    ]
    missing = [name for name in names if not (OUT / name).exists() or (OUT / name).stat().st_size < 1000]
    print("captured", [name for name in names if (OUT / name).exists()])
    print("missing_or_tiny", missing)
    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
