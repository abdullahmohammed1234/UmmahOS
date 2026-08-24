# NVIDIA Live Provider Test

Temporary evaluation report for Phase 12 live NVIDIA evidence extraction.
This does **not** replace offline simulator results or Gemini live attempts.

## NVIDIA Live Provider Test

### Environment

* Provider: NVIDIA NIM hosted API (`https://integrate.api.nvidia.com/v1/chat/completions`)
* Model: `meta/llama-3.3-70b-instruct`
* Prompt: P-003 / `evidence_v3` (unchanged)
* API: live
* Simulator: not used
* Gemini: not used
* Holdout: frozen `HOLDOUT_IDS` (full 30-case holdout **not started**)

### Smoke Test

Not recorded as a separate successful live lucky-guess pass in this run.
Provider connectivity was attempted via the representative probe path using the same
NVIDIA client, model, and P-003 prompt.

### Representative Probe

Planned frozen cases:

* `A-010` lucky guess
* `B-010` strong correct reasoning
* `G-006` weak reasoning
* `D-009` misconception
* `E-009` uncertainty
* `J-008` injection resistance

Completed: **3 / 6** (`A-010`, `B-010`, `G-006`)

All three completed attempts failed at the provider boundary:

| Case | Source | Schema valid | Failure | AdaptiveTutor decision |
|------|--------|--------------|---------|------------------------|
| A-010 | `DETERMINISTIC_FALLBACK` | NO | `LLM_TIMEOUT` | `GATHER_EVIDENCE` |
| B-010 | `DETERMINISTIC_FALLBACK` | NO | `LLM_TIMEOUT` | `GATHER_EVIDENCE` |
| G-006 | `DETERMINISTIC_FALLBACK` | NO | `LLM_TIMEOUT` | `GATHER_EVIDENCE` |

Stop reason: **3 consecutive provider failures** (`LLM_TIMEOUT`).

Fallback was labeled `DETERMINISTIC_FALLBACK`, never `NVIDIA`.
No NVIDIA evidence JSON was accepted for these cases.

### Full Holdout

**LIVE NVIDIA HOLDOUT: INCOMPLETE**

* Planned: 30
* Completed: 0 (holdout not started after probe failure)
* Reason: representative probe stopped on consecutive NVIDIA timeouts
* Provider error: `LLM_TIMEOUT` / “NVIDIA request timed out”
* No full-holdout score is claimed
* Extraction / validity / injection / traceability / workflow rates are **not** reported as a holdout score

Artifact: `results/phase12/live-nvidia-probe/metrics.json`

### Architecture

Confirmed by implementation and probe behavior:

* NVIDIA is only an evidence-extraction provider behind the existing `LLMClient` interface.
* Schema validation remains active before AdaptiveTutor.
* AdaptiveTutor remains authoritative for state, strategy, and challenge selection.
* NVIDIA cannot directly choose `INCREASE` / `PROBE` / `REMEDIATE`.
* Deterministic fallback remains explicitly labeled `DETERMINISTIC_FALLBACK`.
* P-003 / `evidence_v3` was not rewritten for NVIDIA.
* Offline historical Phase 12 results were not overwritten.

### Security

* `.env` is gitignored
* `NVIDIA_API_KEY` is not committed
* No API key appears in this report or probe metrics
