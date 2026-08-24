# Architecture

ADAPT separates **evidence interpretation** from **adaptive policy**.

```text
Human
  ↓
LLM (Gemini) — evidence only
  ↓
Evidence JSON
  ↓
Validation
  ↓
AdaptiveTutor
  ↓
Strategy
  ↓
Challenge
```

Fallback:

```text
LLM unavailable / invalid / timeout
  ↓
DETERMINISTIC_FALLBACK
  ↓
deterministic EvidenceAnalyzer
  ↓
AdaptiveTutor
```

---

## LLM responsibility

**Evidence interpretation.**

Fill a constrained schema: correctness, reasoning quality, confidence, error type, misconception, evidence strength, uncertainty, supporting quotes.

The LLM does not own strategy or the next catalog item.

Primary competition model: Google Gemini (configurable; default `gemini-2.0-flash`). Offline scores used a simulator. Live Gemini 2.5 / 3.6 holdouts are incomplete and must not be drawn as one result.

---

## AdaptiveTutor responsibility

**Adaptive policy.**

Given validated (or fallback) evidence:

1. Update learner state
2. Select instructional strategy
3. Select the next challenge from the catalog

This path is deterministic for a fixed seed. Gemini cannot override it. Strategy tokens in model output are validation failures.

---

## Why this boundary matters

If Gemini both interpreted the learner and chose INCREASE, the system would be a single-prompt tutor with extra JSON. The competition comparison would collapse. The Phase 1–3 engine tests would no longer apply to the decision the learner sees.

The boundary makes prompt engineering testable (does the model extract evidence? does it resist injection?) without giving the model adaptive authority.

---

## Fallback

Provider failure is expected. The product remains usable without a key. The UI must say **Deterministic fallback evidence analysis** when that path ran, and **AI-assisted evidence analysis** only when a live LLM source actually succeeded (`GEMINI` or `NVIDIA`).

---

## Research Mode

Optional judge view of the causal chain. Does not change AdaptiveTutor. Does not display API keys.

When the LLM path is enabled, the chain is:

Human Input → Gemini Evidence → Validation → Learner State → Strategy → Next Challenge

---

## Product boundary

`ProductService` → `AdaptiveTutor`. The Next.js UI displays engine decisions; it does not reimplement them. Phase 12 injects `LLMEvidenceAnalyzer` when credentials are present (`python -m app` enables Gemini if `GEMINI_API_KEY` is set, unless `ADAPT_USE_GEMINI` is off).

NVIDIA is an optional `LLMClient` for scripts/smoke/holdout tooling, not the default product server path.
