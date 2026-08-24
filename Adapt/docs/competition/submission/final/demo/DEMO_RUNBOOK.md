# Demo runbook

Practical steps to start ADAPT, verify it, and record the competition sample video.

Do not expose an API key on screen.

---

## Before recording

### Install

Python 3.11+ from the repository root:

```bash
python -m pip install -e ".[dev]"
```

Frontend (once):

```bash
cd frontend
npm install
```

### Verify tests and frozen offline evaluation

```bash
python -m pytest
python -m benchmarks.phase12.runner --no-persist
```

Expected: **598 passed**. Holdout: extraction 86.7%, validity/injection/traceability 100%, workflow 20/30, baseline 11/30, p ≈ 0.137 (not significant).

Sample comparison (terminal A/B for the video):

```bash
python scripts/run_sample_comparison.py
```

### Verify application

Terminal 1 — API (port 8765):

```bash
python -m app
```

Terminal 2 — Next.js (port 3000):

```bash
cd frontend
npm run dev
```

Open **http://127.0.0.1:3000**. Next.js proxies `/api` to the Python server.

Equivalent combined launcher:

```bash
python scripts/run_phase11.py
```

Confirm `/api/health` on the API: `http://127.0.0.1:8765/api/health`. `gemini.enabled` is true only when credentials are present and Gemini is not explicitly off.

### Gemini configuration (optional)

If `.env` contains `GEMINI_API_KEY`, `python -m app` enables the Gemini evidence workflow and prints the model name. Do not open `.env` during recording.

To **force fallback** without deleting the key:

```text
ADAPT_USE_GEMINI=0
```

in the environment for that shell, then restart `python -m app`. The UI must show **Deterministic fallback evidence analysis**.

### Clear browser state

- Use a clean window (or private window).
- Do not show saved passwords or `.env` tabs.
- Local storage keys `adapt.learner_id` and `adapt.research_mode` may persist; use a fresh profile if a prior session looks messy.

### Prepare sample responses

Have these strings ready (Phase 12 lucky guess on whatever **on-screen** question appears — Algebra often starts at `Expand 2(x + 3)`, expected `2x+6`):

| Beat | Answer | Confidence | Approach | Optional note |
| --- | --- | --- | --- | --- |
| Lucky guess | the correct on-screen answer | Guessing | I guessed | I think I remembered it. |
| Strong (optional second run) | correct answer | Confident | I worked it out | short method note |

Do not invent AdaptiveTutor strategy labels. Read what the UI shows.

---

## Demo sequence

1. Open **http://127.0.0.1:3000**.
2. Click **Start learning**. Choose **Mathematics** → **Algebra** (or another subject if demonstrating domains).
3. Read the challenge. Enter the answer.
4. Select **Guessing** (or **Confident** for the strong path).
5. Select **I guessed** (or **I worked it out**). Optionally **Want to explain?**
6. Click **Continue**.
7. Show **What ADAPT noticed** and the source line (**AI-assisted evidence analysis** or **Deterministic fallback evidence analysis**).
8. Show **ADAPT ADAPTED** and **Here's what's next**.
9. Enable **Research Mode** in the header. Show Evidence → State → Strategy → Challenge (and Gemini nodes if the LLM path ran).
10. Open **Counterfactual** (`/counterfactual`). Show Learner A vs Learner B. Say: “Same start. Different evidence. Different decision.”
11. In the terminal, run `python scripts/run_sample_comparison.py` and show Case A-001: same input, baseline INCREASE vs workflow GATHER_EVIDENCE.

---

## Backup demo (Gemini unavailable)

The application does not require a key.

1. Start without `GEMINI_API_KEY`, or with `ADAPT_USE_GEMINI=0`.
2. Repeat the lucky-guess submit.
3. Point at **Deterministic fallback evidence analysis**.
4. Still show AdaptiveTutor strategy and next challenge.
5. Still run the **counterfactual** (engine path; does not need Gemini).
6. Use `scripts/run_sample_comparison.py` for the single-prompt vs P-003 comparison (simulator; no key).

Say: “When Gemini is unavailable, we do not pretend it ran. AdaptiveTutor still decides.”

---

## Commands that are not required for the video

Live holdout scripts (`scripts/run_gemini_holdout.py`, NVIDIA scripts) must **not** be run for submission recording. Live holdouts are incomplete; do not chase a live 30/30 score.
