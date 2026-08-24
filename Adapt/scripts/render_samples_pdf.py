"""One-off: Markdown samples doc -> HTML -> PDF via Edge headless.

Does not modify application code. Temporary HTML is deleted after PDF creation.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[1]
MD_PATH = ROOT / "docs/competition/submission/final/samples/ADAPT_SAMPLES_AND_COMPARISON.md"
HTML_PATH = ROOT / "docs/competition/submission/final/samples/_adapt_samples_tmp.html"
PDF_PATH = ROOT / "docs/competition/submission/final/samples/ADAPT_SAMPLES_AND_COMPARISON.pdf"

CSS = """
@page { size: Letter; margin: 18mm 16mm; }
:root {
  --ink: #1a1f2e;
  --muted: #4b5568;
  --line: #d7dde8;
  --accent: #0f4c81;
  --soft: #f3f6fb;
  --callout: #eef6ff;
}
* { box-sizing: border-box; }
html, body {
  font-family: "Segoe UI", "Calibri", "Helvetica Neue", Arial, sans-serif;
  color: var(--ink);
  font-size: 10.5pt;
  line-height: 1.45;
  margin: 0;
  padding: 0;
  background: white;
}
.wrap { max-width: 780px; margin: 0 auto; padding: 8px 4px 24px; }
h1 {
  font-size: 22pt;
  line-height: 1.2;
  margin: 0 0 6px;
  color: var(--accent);
  border-bottom: 3px solid var(--accent);
  padding-bottom: 10px;
}
h2 {
  font-size: 14pt;
  margin: 26px 0 10px;
  color: var(--accent);
  border-bottom: 1px solid var(--line);
  padding-bottom: 4px;
  page-break-after: avoid;
}
h3 {
  font-size: 12pt;
  margin: 18px 0 8px;
  color: #16324f;
  page-break-after: avoid;
}
h4 {
  font-size: 11pt;
  margin: 14px 0 6px;
  color: #243447;
}
p { margin: 0 0 10px; }
ul, ol { margin: 0 0 12px 18px; padding: 0; }
li { margin: 3px 0; }
blockquote {
  margin: 12px 0;
  padding: 10px 14px;
  background: var(--callout);
  border-left: 4px solid var(--accent);
  color: #16324f;
}
blockquote p { margin: 0; }
code {
  font-family: Consolas, "Courier New", monospace;
  font-size: 9.2pt;
  background: var(--soft);
  padding: 1px 4px;
  border-radius: 3px;
}
pre {
  background: #0f172a;
  color: #e2e8f0;
  padding: 12px 14px;
  border-radius: 6px;
  overflow-x: auto;
  font-size: 8.8pt;
  line-height: 1.35;
  page-break-inside: avoid;
}
pre code { background: transparent; color: inherit; padding: 0; }
table {
  width: 100%;
  border-collapse: collapse;
  margin: 10px 0 14px;
  font-size: 9.5pt;
  page-break-inside: avoid;
}
th, td {
  border: 1px solid var(--line);
  padding: 6px 8px;
  vertical-align: top;
  text-align: left;
}
th {
  background: var(--soft);
  color: #16324f;
  font-weight: 600;
}
hr {
  border: none;
  border-top: 1px solid var(--line);
  margin: 18px 0;
}
strong { color: #122033; }
.banner {
  background: linear-gradient(135deg, #0f4c81 0%, #1f6f8b 100%);
  color: white;
  padding: 18px 20px;
  border-radius: 8px;
  margin-bottom: 18px;
}
.banner .sub { opacity: 0.95; margin-top: 4px; font-size: 11pt; }
.banner .tagline {
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px solid rgba(255,255,255,0.35);
  font-style: italic;
  font-size: 11pt;
}
.meta {
  color: var(--muted);
  font-size: 9.5pt;
  margin-bottom: 16px;
}
@media print {
  a { color: inherit; text-decoration: none; }
  .banner, th, blockquote, pre, code {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
}
"""


def find_edge() -> Path:
    candidates = [
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError("Edge/Chrome not found for headless PDF print")


def main() -> int:
    md = MD_PATH.read_text(encoding="utf-8")
    md_clean = re.sub(
        r"```mermaid[\s\S]*?```",
        "_See the textual workflow diagrams above._\n",
        md,
    )
    parser = (
        MarkdownIt("commonmark", {"breaks": True, "html": True})
        .enable("table")
        .enable("strikethrough")
    )
    body = parser.render(md_clean)
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>ADAPT — Workflow Samples &amp; Single-Prompt Comparison</title>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
  <div class="banner">
    <div style="font-size:20pt;font-weight:700;">ADAPT — Workflow Samples &amp; Single-Prompt Comparison</div>
    <div class="sub">ML Prompt Engineering Track</div>
    <div class="tagline">Gemini interprets learner evidence. AdaptiveTutor decides how to adapt.</div>
  </div>
  <div class="meta">Competition samples document · Offline simulator recordings · Not a live Gemini scorecard</div>
  {body}
</div>
</body>
</html>
"""
    html = re.sub(
        r"<h1>ADAPT — Workflow Samples &amp; Single-Prompt Comparison</h1>\s*"
        r"<p><strong>ML Prompt Engineering Track</strong></p>\s*"
        r"<blockquote>\s*<p>Gemini interprets learner evidence\. AdaptiveTutor decides how to adapt\.</p>\s*</blockquote>",
        "",
        html,
        count=1,
    )
    HTML_PATH.write_text(html, encoding="utf-8")

    browser = find_edge()
    if PDF_PATH.exists():
        PDF_PATH.unlink()
    uri = HTML_PATH.resolve().as_uri()
    cmd = [
        str(browser),
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={PDF_PATH}",
        uri,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if not PDF_PATH.exists():
        print(proc.stdout)
        print(proc.stderr, file=sys.stderr)
        raise SystemExit(f"PDF was not created (exit {proc.returncode})")

    HTML_PATH.unlink(missing_ok=True)
    size_kb = PDF_PATH.stat().st_size / 1024
    print(f"Wrote {PDF_PATH} ({size_kb:.1f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
