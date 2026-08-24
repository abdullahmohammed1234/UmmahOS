# Known limitations

ADAPT is an engineering prototype. Weaknesses are documented, not hidden.

1. **Phase 1F fraction subtraction boundary (G-001-B).** Three successes on a subtraction item with add-numerator reasoning did not accumulate to INCREASE. Domain transfer on that item is incomplete.

2. **Phase 1F delayed misconception vs regression (G-003).** Historical runs used DECREASE instead of diagnostic probing. Phase 2 later separated that case; the Phase 1F result remains historical evidence.

3. **Phase 5 human participants = 0.** H1 is INCONCLUSIVE. This is not a positive learning result.

4. **Phase 4 formative usability study incomplete.** Planned 5-learner usability remains PENDING (0 / 5).

5. **No claim of educational efficacy.** Engineering benchmarks are not proof that learners learn more.

6. **Heuristic evidence analysis, with optional Gemini interpretation.** The frozen analyzer is deterministic and cue-based. Phase 12 may wrap it with a Gemini evidence workflow. Gemini does not choose strategy or the next challenge. Offline Phase 12 scores used a prompt simulator unless a live key is requested.

7. **Limited concepts.** Curated multi-domain catalog; not a complete curriculum.

8. **Small challenge bank.** Next-challenge choice is constrained. Unavailable items are surfaced rather than invented.

9. **Phase 12 holdout vs single-prompt baseline is not statistically significant** (n = 30, McNemar p ≈ 0.137). Prompt-version differences were measured; educational efficacy was not.

## Live provider status (added 2026-08-20 freeze audit)

10. **Live Gemini holdout incomplete** (quota/rate limits). Do not claim a full live Gemini 30/30 score or combine Gemini 2.5 / 3.6 partial attempts.

11. **Live NVIDIA holdout incomplete** (provider timeouts on representative probes for `meta/llama-3.3-70b-instruct`). Classify as `LIVE NVIDIA HOLDOUT: INCOMPLETE`, not as 0% extraction accuracy.

12. Offline Phase 12 simulator results remain the reproducible quantitative evidence. Gemini/NVIDIA are optional evidence interpreters; AdaptiveTutor retains adaptive control.

## Next research steps

- Run the Phase 5 protocol with consented learners.
- Complete the Phase 4 usability protocol.
- Expand the challenge bank without changing the frozen decision rules until a new research phase is declared.
- Revisit the G-001-B fraction-subtraction evidence boundary with better items, not by recoding the historical label.
