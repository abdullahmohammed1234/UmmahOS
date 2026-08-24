# Limitations

Professional constraints on what this submission claims.

1. **Phase 5 remains inconclusive.** Human learning evaluation: INCONCLUSIVE, **n = 0**.
2. **No learning-gain claim is made.** Engineering benchmarks are not proof that learners learn more.
3. **Offline holdout is the primary reproducible quantitative evaluation.** Backend: prompt-simulator. Selected prompt: P-003 / `evidence_v3`. n = 30.
4. **Gemini live holdout was incomplete due to provider quota/rate limits.** Smoke and partial runs succeeded; no full live Gemini score is claimed.
5. **Gemini 2.5 and 3.6 attempts are not combined.** They are separate incomplete provider-validation attempts.
6. **NVIDIA live holdout was incomplete due to timeouts.** Model: `meta/llama-3.3-70b-instruct`. Representative probes: 3/3 timeout → deterministic fallback. Full holdout: 0/30.
7. **No live-provider score is claimed.** Do not quote a live accuracy percentage.
8. **Partial live attempts are not treated as official holdout results.** Including any `n: 30` metrics file written after rate-limit interruption.
9. **The system uses deterministic fallback** when LLM inference is unavailable or invalid. Fallback is never labeled as a successful LLM result.
10. **P-003 and the holdout are frozen.** AdaptiveTutor decision logic, strategy, challenge selection, `evidence_v3`, and holdout IDs were not retuned for submission.

Additional documented limits (unchanged historical engineering):

- Holdout workflow vs baseline is **not statistically significant** (McNemar p ≈ 0.137).
- Offline simulator JSON is not a Gemini leaderboard.
- Challenge bank is finite; items are selected, not generated.
- First-step `GATHER_EVIDENCE` often disagrees with family labels that expected an immediate INCREASE or REMEDIATE.
- Phase 4 formative usability remains PENDING (0 / 5).
