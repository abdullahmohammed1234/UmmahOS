# Phase 12 Freeze Audit

**Date:** 2026-08-20  
**Scope:** Competition-readiness audit and freeze. No AdaptiveTutor redesign. No P-003 / `evidence_v3` / holdout retuning. No new LLM provider.

## Phase 12 Freeze Audit

### Overall status

```text
READY WITH LIMITATIONS
```

The offline Phase 12 evidence, adaptive-policy boundary, fallback labeling, product causal chain, Research Mode, and counterfactual demo are competition-ready. Live Gemini and live NVIDIA holdouts remain incomplete provider-validation attempts and must not be oversold.

### Core engine

* **Tests:** `598 passed` (`python -m pytest`, 2026-08-20 freeze run). Prior known baseline was `596 passed`; **+2** targeted product labeling tests were added during this audit (`test_nvidia_success_is_labeled_ai_assisted_not_fallback`, `test_unavailable_llm_is_labeled_fallback_not_ai`). No artificial padding.
* **AdaptiveTutor status:** Unchanged. Default analyzer remains deterministic `EvidenceAnalyzer`. LLM path is an optional `LLMEvidenceAnalyzer` adapter.
* **Frozen decision logic:** State update, strategy, and challenge selection remain under AdaptiveTutor. Schema validation rejects adaptive-decision fields (`strategy`, `next_challenge`, strategy tokens, etc.). Existing boundary tests in `tests/phase12/test_engine_boundary.py` still pass.

### Phase 12 evaluation

#### Offline development

* Prompts compared: P-001 (`evidence_v1`), P-002 (`evidence_v2`), P-003 (`evidence_v3`)
* Selection: **P-003 / `evidence_v3`** on frozen development criteria
* P-002 retained as a failed injection case (development injection robustness 0.000)

#### Offline holdout (reproduced this audit)

Command:

```bash
python -m benchmarks.phase12.runner --no-persist
```

Frozen result (backend `prompt-simulator`, seed `20260819`):

| Metric | Value |
| --- | --- |
| Selected prompt | `evidence_v3` (P-003) |
| Holdout n | 30 |
| Extraction | 86.7% (0.866…) |
| Validity | 100% |
| Injection resistance | 100% |
| Traceability | 100% |
| Workflow | 20/30 (0.667) |
| Baseline | 11/30 (0.367) |
| McNemar p | ≈ 0.137 |
| Statistically significant | **False** |

Interpretation frozen: workflow advantage is **not** statistically significant. Do not claim that Gemini/an LLM makes ADAPT smarter. Do not claim learning gain.

#### Prompt selection / honesty

* Offline scores use a prompt-conditioned simulator, not live Gemini completions.
* Historical `results/phase12/report.md` was **not** overwritten.

### Live providers

#### Gemini

* **Status:** Live API usable for smoke / partial holdout; **full live holdout incomplete**.
* **Attempts (do not combine):**
  * Gemini 2.5 Flash — real calls succeeded; smoke passed; partial holdout begun; quota/rate limit stopped completion. Artifact labeled `results/phase12/live-gemini-holdout/metrics-quota-exhausted-attempt.json`.
  * Gemini 3.6 Flash — probe passed; partial live holdout reached 9/30 workflow cases (8 Gemini successes, 1 deterministic fallback); rate limit stopped the run; **no full live score**.
* **Limitation:** Do not invent a live Gemini percentage from partial attempts. Do not merge 2.5 and 3.6 results.

#### NVIDIA

* **Status:** `LIVE NVIDIA HOLDOUT: INCOMPLETE`
* **Provider / model:** NVIDIA NIM · `meta/llama-3.3-70b-instruct`
* **Probe:** 3 representative attempts → 3 timeouts → 3 `DETERMINISTIC_FALLBACK` (never labeled `NVIDIA`)
* **Full holdout:** 0/30 started after probe stop
* **Limitation:** This is **not** an extraction accuracy of 0%. Reason: provider timeout. Documented in `docs/phase-12/12-nvidia-live-test.md` and `results/phase12/live-nvidia-probe/`.

Default product server enables Gemini when `GEMINI_API_KEY` is present (`src/app/server.py`). NVIDIA remains an explicit `LLMClient` option for scripts/smoke/holdout tooling.

### Product

* **Learner flow:** Topic → challenge → answer → confidence → reasoning → evidence analysis → learner state → strategy → next challenge → adaptation explanation. Verified via `ProductService` during this audit.
* **AI-assisted evidence analysis:** Shown for live LLM sources (`GEMINI`, `NVIDIA`). Audit fixed a gap where `NVIDIA` success omitted the learner-facing label on the step payload.
* **Fallback:** Unavailable / timeout / invalid JSON → `DETERMINISTIC_FALLBACK` with explicit “Deterministic fallback evidence analysis” label. Never presented as Gemini/NVIDIA success.
* **Research Mode:** Exposes evidence source, workflow nodes, state, strategy, next challenge, and explanations. Does not expose API keys.
* **Counterfactuals:** Live engine; different evidence → different decisions (`INCREASE` vs `PROBE` in default demo). Not hardcoded UI tables.
* **Multi-domain inventory (unchanged):** 7 subjects, 64 topics, 248 challenges — mathematics, calculus, computer-science, physics, chemistry, space, quantum. No domains added or rewritten in this audit.

### Security

* `.env` is gitignored and **not tracked**.
* No hard-coded API keys found in source.
* Live metrics artifacts checked: no `nvapi-` / key material embedded.
* Provider clients redact secrets in error paths.
* **Git hygiene note (pre-existing):** ~62 `__pycache__` / `.pyc` files are still tracked despite `.gitignore`. They do not contain secrets, but should be untracked in a future hygiene commit (not done here; no commit in this audit).
* `frontend/.next` build outputs appear untracked (good). Do not commit them.

### Reproducibility

Exact offline commands (no API keys required):

```bash
python -m pytest
python -m benchmarks.phase12.runner --no-persist
```

Live scripts (optional; require keys; not part of CI):

* `scripts/run_gemini_smoke_test.py`
* `scripts/run_gemini_holdout.py`
* `scripts/run_nvidia_smoke_test.py`
* `scripts/run_nvidia_holdout.py`

CI / default pytest path uses mocks or the prompt simulator. Default `ProductService()` does not enable Gemini. Offline benchmark defaults to `prompt-simulator` unless `--live` is requested.

### Live / offline separation (verified)

| Mode | Source label | Notes |
| --- | --- | --- |
| Offline simulator / mock | `GEMINI` only when mock provider is gemini-like success path | Benchmark simulator is labeled as simulator backend in reports |
| Live Gemini success | `GEMINI` | Requires credentials + successful validated JSON |
| Live NVIDIA success | `NVIDIA` | Requires explicit NVIDIA client |
| Provider unavailable / timeout | `DETERMINISTIC_FALLBACK` | Never labeled as LLM success |
| Invalid LLM JSON | `LLM_VALIDATION_FAILURE` then fallback | Existing contract |

### Adaptive-policy boundary (verified)

* LLM schema is evidence-only.
* `strategy: "REMEDIATE"` (and equivalents) rejected → fallback; AdaptiveTutor still decides.
* `next_challenge` cannot select the next item.
* Challenge selection remains catalog/selector controlled.

### Competition limitations

Explicitly state in demos and submission text:

* **No learning-gain claim**
* **Phase 5 remains INCONCLUSIVE (n = 0)**
* **Live provider holdouts are incomplete**
* **Offline Phase 12 results are the reproducible quantitative evidence**
* **McNemar p ≈ 0.137 — not statistically significant**
* Gemini/NVIDIA are **optional evidence interpreters**; ADAPT retains deterministic adaptive control

### Architecture freeze

After this audit, treat as frozen:

* AdaptiveTutor decision logic
* Strategy / challenge selection
* P-003 / `evidence_v3`
* Offline holdout set and expected offline scores
* Historical Phase 12 / Phase 5 artifacts (append-only corrections only)

### Changes made in this audit

1. `src/adapt/product/service.py` — unify evidence-source labeling so `NVIDIA` success shows **AI-assisted evidence analysis**, and fallback never impersonates an LLM.
2. `tests/phase12/test_product.py` — two labeling verification tests (+2 to suite).
3. `docs/competition/submission/limitations.md` — dated live-provider incompleteness section.
4. `docs/competition/limitations.md` — matching dated live-provider notes.
5. `docs/competition/submission/samples.md` — clarify offline samples vs incomplete live artifacts.
6. `docs/phase-12/12-freeze-audit.md` — this report.

No historical benchmark reports were rewritten. No provider experiment was started.
