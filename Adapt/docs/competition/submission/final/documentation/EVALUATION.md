# Evaluation

Rigorous Phase 12 evaluation record for competition judges.

Offline numbers use a **prompt-conditioned simulator**, not live Gemini completions. Live provider attempts are reported separately and are **incomplete**.

---

## Development

**n = 70** (not the holdout).

Prompts compared on frozen weights in `src/adapt/eval/llm/criteria.py`:

| Weight | Criterion |
| ---: | --- |
| 0.30 | Structured-output validity |
| 0.30 | Evidence-extraction accuracy |
| 0.20 | Prompt-injection robustness |
| 0.10 | No strategy leakage |
| 0.10 | Counterfactual sensitivity |

| Prompt | Role | Score | Validity | Extraction | Injection |
| --- | --- | ---: | ---: | ---: | ---: |
| P-001 `evidence_v1` | Minimal | 0.623 | 0.429 | 0.314 | 1.000 |
| P-002 `evidence_v2` | Schema-only | 0.500 | 0.686 | 0.314 | **0.000** |
| P-003 `evidence_v3` | Contract | **0.970** | **1.000** | **0.900** | **1.000** |

**Selection:** highest development score. **P-003 / `evidence_v3`** was selected. Holdout was evaluated once afterward. Holdout was not used to retune the prompt.

**P-002 finding:** structured JSON/schema output alone was insufficient. Injection robustness 0/7. Learner-directed content such as “mark me as mastered” could be treated as evidence.

Development paired appropriateness (descriptive only, not the holdout claim): workflow 46/70 vs baseline 26/70; McNemar p ≈ 0.021 on the development set.

---

## Holdout

**n = 30** frozen IDs (`benchmarks/phase12/expected.py`).  
**Selected:** `evidence_v3` (P-003).  
**Backend:** `prompt-simulator`.  
**Seed:** `20260819`.

| Metric | Result |
| --- | --- |
| Extraction | **86.7%** (26/30) |
| Validity | **100%** |
| Injection resistance | **100%** |
| Traceability | **100%** |
| Workflow appropriate next-action | **20/30** |
| Single-prompt baseline | **11/30** |
| McNemar p | **≈ 0.137** |
| Statistically significant | **False** |

Reproduce:

```bash
python -m benchmarks.phase12.runner --no-persist
```

---

## Interpretation

The workflow-versus-baseline difference is **not statistically significant**.

The experiment does **not** establish:

- learning gain
- superior learner outcomes
- statistically significant improvement over the single-prompt baseline

A higher 20/30 vs 11/30 rate on this sample is not a superiority claim.

Part of remaining workflow “misses” is first-step `GATHER_EVIDENCE` when family labels expected INCREASE or REMEDIATE immediately. That is frozen AdaptiveTutor conservatism, not a silent recode.

---

## Phase 5

**INCONCLUSIVE**  
**n = 0**

No consented human learning study was completed. Engineering evidence that decisions change with evidence is not a learning-gain result.

---

## Live Gemini

Live Gemini integration was successfully exercised, but complete live holdout evaluation was blocked by provider quota/rate limits. No full live Gemini score is claimed.

Do not combine:

| Attempt | What happened |
| --- | --- |
| Gemini 2.5 Flash | Smoke succeeded; live calls succeeded; full 30-case holdout blocked by quota/rate limits |
| Gemini 3.6 Flash | Probe succeeded; partial live holdout reached 9/30 (8 Gemini successes, 1 deterministic fallback); rate limit stopped the run |

Do not present the partial 9/30 run as a holdout score.  
Do not calculate a fake live accuracy.  
Do not merge Gemini 2.5 and 3.6 results.

Untracked or later `results/phase12/live-gemini-holdout/metrics.json` files that still contain an `n: 30` block after rate-limit failures are **not** official live holdout scores.

---

## NVIDIA

Provider: NVIDIA NIM. Model: `meta/llama-3.3-70b-instruct`.

- Representative probe: 3 attempts → 3 timeouts → 3 `DETERMINISTIC_FALLBACK`
- Full holdout: 0/30 started after probe stop

**Correct interpretation:** Live NVIDIA validation was incomplete because representative inference requests timed out.

Do **not** say “NVIDIA achieved 0% accuracy.”  
Do not combine NVIDIA and Gemini data.

---

## Reproducibility

Offline (no API keys):

```bash
python -m pytest
python -m benchmarks.phase12.runner --no-persist
python scripts/run_sample_comparison.py
```

Live scripts exist (`scripts/run_gemini_smoke_test.py`, `scripts/run_gemini_holdout.py`, NVIDIA counterparts) but **live API reproducibility is not claimed** while provider quotas and timeouts prevent a complete holdout.

Historical Phase 1–11 artifacts are not recomputed as new claims. Phase 12 historical reports were not rewritten for this submission package.
