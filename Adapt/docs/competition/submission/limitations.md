# Phase 12 limitations (competition)

Documented weaknesses. Not hidden.

1. **Phase 5 remains INCONCLUSIVE (n = 0).** Engineering that Gemini can extract evidence is not a learning-gain result. ADAPT has not been shown to improve learning.

2. **Offline Phase 12 scores used a prompt-conditioned simulator**, not live Gemini completions. The simulator follows instruction features in the prompt so P-001/P-002/P-003 can be compared without an API key. Live Gemini is the smoke test (`scripts/run_gemini_smoke_test.py`) when `GEMINI_API_KEY` is set. Do not treat simulator JSON as a Gemini leaderboard.

3. **Holdout baseline comparison is not statistically significant.** n = 30, McNemar p ≈ 0.137. A higher workflow percentage is not a superiority claim.

4. **P-002 failed prompt injection** on the development set (0/7). Structured JSON without a contract is not automatically safe.

5. **First-step GATHER_EVIDENCE** from AdaptiveTutor often disagrees with family labels that expected INCREASE or REMEDIATE immediately. That is the frozen engine’s conservative start, not a silent recode.

6. **Gemini does not generate curriculum.** Next challenges come from the finite catalog via the existing selector.

7. **No API keys in git.** Without credentials the product uses deterministic evidence analysis and says so.

8. Historical Phase 1F boundaries (G-001-B, G-003) and incomplete usability studies are unchanged.

## Live provider status (2026-08-20 freeze audit)

9. **Live Gemini holdout is incomplete.** Real API smoke/probes succeeded on Gemini 2.5 Flash and Gemini 3.6 Flash, but quota/rate limits prevented a full 30/30 live holdout. Do **not** combine model attempts or invent a live Gemini percentage from partial runs.

10. **Live NVIDIA holdout is incomplete.** Provider: NVIDIA NIM, model `meta/llama-3.3-70b-instruct`. Representative probes timed out (3/3) and fell back to `DETERMINISTIC_FALLBACK`. Classification: `LIVE NVIDIA HOLDOUT: INCOMPLETE` (reason: provider timeout). This is **not** an extraction accuracy of 0%.

11. **Gemini/NVIDIA are optional evidence-interpretation providers.** AdaptiveTutor retains deterministic adaptive control for state, strategy, and challenge selection.
