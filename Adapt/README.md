# ADAPT for UmmahOS

Evidence-driven adaptive tutoring for **UmmahOS Academy** community-safety learning.

ADAPT adapts to *how* a learner responds—not just whether an answer is correct—then updates learner state, chooses an instructional strategy, and selects the next challenge.

## UmmahOS integration

UmmahOS uses **only the Python HTTP API**. The Laravel backend proxies session create/submit through `HttpAdaptClient`; the UmmahOS Vue Academy UI (`AdaptPracticePage`) is the learner-facing experience.

```text
UmmahOS Vue (AdaptPracticePage)
        ↓
Laravel API (/academy/.../adapt-sessions)
        ↓
ADAPT Python API (port 8765)
        ↓
Community Safety challenge catalog
```

Start the API:

```bash
python -m app
```

Default URL: [http://127.0.0.1:8765](http://127.0.0.1:8765)

Configure UmmahOS backend (`backend/.env`):

```env
ADAPT_BASE_URL=http://127.0.0.1:8765
ADAPT_TIMEOUT=10
```

## Content

The catalog contains **Community Safety** scenarios aligned with Community Shield learning patterns:

| Topic | Focus |
| --- | --- |
| Understanding Context Before Responding | Context preservation, evidence quality, uncertainty |
| Recognizing Coded Language | Coded references, dog whistles, neutral tone masking |
| Repeated Harassment Patterns | Targeting over time, escalation, bystander role |
| Safe Reporting & Escalation | Approved channels, documentation, urgent threats |
| Privacy & Boundaries | Reporter privacy, need-to-know sharing |

Educational scenarios are sanitized abstractions. They do **not** reproduce raw incident content.

## How it works

```text
Answer → Evidence → Learner State → Strategy → Next Challenge
```

1. **Evidence Analyzer** extracts signals about understanding, confidence, reasoning, and misconceptions.
2. **Learner State** maintains the system's current belief about the learner.
3. **Strategy Engine** chooses how the tutor should respond.
4. **Challenge Selector** turns that strategy into the next task.

## API

| Method | Endpoint |
| --- | --- |
| GET | `/api/health` |
| GET | `/api/subjects` |
| GET | `/api/subjects/{subject_id}` |
| POST | `/api/sessions` |
| GET | `/api/sessions/{id}` |
| POST | `/api/sessions/{id}/responses` |

UmmahOS typically starts sessions with:

```json
{
  "topic_id": "csafety-context",
  "learner_id": "member-123",
  "subject_id": "community-safety",
  "initial_challenge": "CSAFE-CTX-001",
  "max_steps": 10,
  "mode": "learner"
}
```

## Testing

```bash
python -m pytest
```

Internal engine regression tests still use the frozen Phase 3 algebra/fractions bank for historical benchmarks. The **product catalog** exposed through the HTTP API is community-safety only.

## Project structure

```text
Adapt/
├── src/
│   ├── adapt/          # engine, product boundary, community-safety catalog
│   └── app/            # HTTP API
├── app/                # `python -m app` launcher
├── tests/
├── demo/
└── README.md
```

## Limitations

- Heuristic, deterministic evidence analysis by default; optional Gemini evidence workflow when configured.
- Curated community-safety catalog—not a complete curriculum.
- Finite challenge bank; questions are not generated at runtime.
- No claim of educational efficacy without human learning evaluation.
