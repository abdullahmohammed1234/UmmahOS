# Judge questions

Answers match the frozen evidence. Do not upgrade Phase 5 or invent live scores.

---

**Q: Why not let Gemini choose the next question?**

Because that would be a single-prompt tutor. AdaptiveTutor already has a tested policy for state, strategy, and catalog selection. Gemini is an evidence interpreter. If it emitted INCREASE, validation would reject it.

---

**Q: Why do you need prompt engineering?**

Free-form learner text is noisy: guesses, slips, misconceptions, and injection. Prompts were versioned and scored on frozen development criteria. The prompt is the contract that keeps the LLM out of adaptive authority.

---

**Q: What did P-002 teach you?**

Structured JSON / schema output is not enough. P-002 improved validity relative to P-001 but scored **0/7** injection robustness on development. “Mark me as mastered” could be treated as evidence.

---

**Q: What makes P-003 different?**

P-003 adds an evidence contract: untrusted learner delimiters, no automatic mastery, distinguish guessing from reasoning, classify errors, preserve uncertainty, never output a strategy. It won the frozen development score and was evaluated once on holdout.

---

**Q: How do you prevent prompt injection?**

Learner text is data inside `<<<LEARNER_INPUT_START/END>>>`. P-003 says to ignore task-changing instructions. Validation rejects strategy fields. AdaptiveTutor still decides. Recorded J-001: baseline INCREASE; workflow weak evidence, GATHER_EVIDENCE.

---

**Q: What happens if Gemini fails?**

Timeout, rate limit, missing key, or invalid JSON → `DETERMINISTIC_FALLBACK` → existing EvidenceAnalyzer → AdaptiveTutor. The UI says **Deterministic fallback evidence analysis**. That is not a Gemini success.

---

**Q: Is the system actually adaptive?**

Yes, in the engineering sense: evidence updates state; state selects strategy; strategy selects the next challenge. The counterfactual holds the start fixed and changes evidence; the decision changes.

---

**Q: How do you know the adaptation came from learner evidence?**

Research Mode shows the chain and evidence source. The counterfactual uses the live engine, not a hardcoded table. Different evidence produces different mastery and, over the recorded three-step path, INCREASE vs PROBE.

---

**Q: Did you prove learning gains?**

No. Phase 5 is **INCONCLUSIVE, n = 0**.

---

**Q: Did the workflow significantly outperform the baseline?**

No. Offline holdout 20/30 vs 11/30, McNemar **p ≈ 0.137**. Not statistically significant.

---

**Q: Which model did you use?**

Primary competition LLM: Google Gemini. Code default: `gemini-2.0-flash` (`GEMINI_MODEL`). Live calls were also exercised on Gemini 2.5 Flash and Gemini 3.6 Flash. Offline scores used a prompt simulator. Those live attempts are not combined into one score.

---

**Q: Did you test live Gemini?**

Yes, integration was exercised. Complete live holdout evaluation was blocked by quota/rate limits. No full live Gemini score is claimed. Partial 9/30 is not a holdout score.

---

**Q: Did you test NVIDIA?**

Yes, NVIDIA NIM `meta/llama-3.3-70b-instruct`. Representative probes timed out (3/3) and fell back. Full holdout 0/30. Incomplete because of timeouts — not “0% accuracy.”

---

**Q: What is deterministic about ADAPT?**

AdaptiveTutor: state update, strategy, and challenge selection. Same seed and evidence → same decision. The LLM path is optional and validated.

---

**Q: Can the system work without an LLM?**

Yes. Default without credentials is deterministic evidence analysis. The product remains usable offline.

---

**Q: What would you improve next?**

Complete live holdouts only if provider capacity allows — without retuning P-003 against the frozen holdout. Run Phase 5 with consented learners. Keep AdaptiveTutor frozen until a new research phase is declared.
