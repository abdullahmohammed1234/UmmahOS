# UmmahOS

**Community infrastructure for Muslim student organizations.**

> **AI assists. Humans decide.**

> A community safety report should not end with a screenshot.

---

## GNCI Hackathon Submission

| Field | Value |
|-------|--------|
| **Project** | UmmahOS |
| **Core idea** | A community safety report should not end with a screenshot. |
| **Repository** | [https://github.com/abdullahmohammed1234/UmmahOS](https://github.com/abdullahmohammed1234/UmmahOS) |
| **Live demo** | Run locally — see [Quick start](#quick-start) below |
| **Demo instructions** | [docs/DEMO_RUNBOOK.md](docs/DEMO_RUNBOOK.md) |
| **Architecture** | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| **Scorecard mapping** | [docs/JUDGING.md](docs/JUDGING.md) |
| **Submission checklist** | [docs/GNCI_SUBMISSION.md](docs/GNCI_SUBMISSION.md) |

**No video submission.** This repository is designed to stand on its own: README, screenshots, documentation, and a reproducible local demo.

**Demo password** (all seeded accounts): `password`

---

## The problem

Muslim Student Associations manage members, events, resources, education, and community safety across disconnected tools:

**Forms · Screenshots · Spreadsheets · Messaging apps · Disconnected reports**

When something concerning happens online, context disappears before a trained reviewer ever sees it. Outcomes are hard to track. Learning rarely returns to the community.

## The idea

Instead of a screenshot alone, UmmahOS preserves **context** through a structured workflow:

```text
REPORT
  ↓
CONTEXT
  ↓
AI ASSISTANCE
  ↓
HUMAN REVIEW
  ↓
EVIDENCE
  ↓
OUTCOME
  ↓
LEARNING
  ↓
ADAPT
```

## How it works

1. A member **reports a concern** with platform, original item, surrounding context, replies, and related copies.
2. Optional **Gemini advisory analysis** surfaces signals, classification, confidence, and uncertainty — it does not decide.
3. A trained **human reviewer** confirms, marks uncertain, requests context, escalates, or closes.
4. An **evidence package** (JSON/PDF) can be exported for documentation — it is not auto-submitted anywhere.
5. **Outcome tracking** answers “What happened next?” for members (reporter-visible summaries only).
6. Confirmed patterns can become **Academy** lessons and **ADAPT** adaptive practice.

## Community Shield

Community Shield is the flagship. It captures structured evidence, not just a crop of a post:

| Field | Purpose |
|-------|---------|
| Incident | What happened |
| Platform | Where it appeared |
| Original item | The reported content |
| Context | Surrounding conversation |
| Replies | Responses that change meaning |
| Related items | Cross-posts or copies |
| Language | Translation/context notes |
| Notes | Reporter notes |
| Classification | Human determination |

**Context changes everything.**

## AI + human oversight

| AI (advisory) | Human (authoritative) |
|---------------|----------------------|
| Potential signals | Confirm |
| Classification | Mark Uncertain |
| Confidence | Request Context |
| Uncertainty | Escalate |
| Recommended action | Close |

**Uncertainty is a valid outcome.** There is no automatic enforcement.

## Outcome tracking

UmmahOS does not stop at “report submitted.”

**Reported → Under Review → Decision → Outcome → Appeal / Correction**

Members see reporter-visible updates. Internal reviewer notes stay private.

## Evidence packages

Authorized reviewers can preview and export a structured **Evidence Package**:

Incident · Context · Related Evidence · AI Analysis · Uncertainty · Human Review · Outcome · Reporting Route · Safety & Privacy

> Exporting creates a report. It does not automatically submit it.

## Academy + ADAPT

**Confirmed Pattern → Academy Lesson → Scenario → Learner Response → ADAPT → Next Challenge**

ADAPT uses the learner’s answer, confidence, and reasoning. The UI shows **What ADAPT noticed** and **Why this question?** from the real ADAPT integration.

## Multi-MSA architecture

One deployment, many isolated organizations:

```text
UmmahOS
├── Demo MSA Alpha
├── Demo MSA Beta
└── Demo MSA Gamma
```

Each MSA has isolated members, events, reports, evidence, reviews, Academy, and outcomes. Sign in as `multi.user@example.com` and switch organizations to see **reviewer in Alpha** vs **admin in Beta** — navigation, permissions, and content all change.

## Ethics and safety

- AI is advisory
- Human review is authoritative
- Uncertainty is explicit
- Private information stays protected
- No automatic enforcement
- Synthetic evaluation tests safety properties (not live AI accuracy)

## Synthetic evaluation

Reproducible synthetic safety evaluation for Community Shield:

| Metric | Result |
|--------|--------|
| Scenarios | **42** |
| Categories | **7** |
| Critical failures | **0** |

```bash
cd backend && php artisan community-shield:evaluate
```

This verifies context preservation, uncertainty handling, human routing, privacy isolation, and no automatic enforcement. It does **not** claim real-world AI detection accuracy.

See [docs/PHASE_10.md](docs/PHASE_10.md) and [docs/evaluation/SYNTHETIC_EVALUATION.md](docs/evaluation/SYNTHETIC_EVALUATION.md).

## Screenshots

Capture these locally after `php artisan migrate --seed` (see [docs/screenshots/README.md](docs/screenshots/README.md)). Add files to `docs/screenshots/` and they will render below.

| | |
|---|---|
| ![Landing page](docs/screenshots/01-landing.png) | ![Community Shield](docs/screenshots/02-community-shield.png) |
| ![Context](docs/screenshots/03-context.png) | ![AI analysis](docs/screenshots/04-ai-analysis.png) |
| ![Human review](docs/screenshots/05-human-review.png) | ![Evidence package](docs/screenshots/06-evidence-package.png) |
| ![Outcome tracking](docs/screenshots/07-outcome.png) | ![Academy + ADAPT](docs/screenshots/08-academy-adapt.png) |
| ![Multi-MSA](docs/screenshots/09-multi-msa.png) | |

*Images appear after manual capture — placeholders above until files exist.*

## Judge demo (3–5 minutes)

**Start:** [http://localhost:5173/welcome](http://localhost:5173/welcome)

| Time | What to show |
|------|----------------|
| 0:00 | Landing — problem, **AI assists. Humans decide.** |
| 0:20 | Community Shield landing — Capture → Outcome workflow |
| 0:40 | Structured context (report or seeded My Report) |
| 1:10 | Review queue → context relationship view |
| 1:40 | AI Analysis — advisory, uncertainty visible |
| 2:00 | Human Review — Confirm / Uncertain / … |
| 2:40 | Evidence Package — export disclaimer |
| 3:00 | My Reports — **What happened next?** |
| 3:20 | Academy → Community Safety |
| 3:40 | ADAPT practice |
| 4:00 | `multi.user@example.com` — switch Alpha ↔ Beta |

Full script: [docs/DEMO_RUNBOOK.md](docs/DEMO_RUNBOOK.md)

**Accounts:** `alpha.member@example.com` · `alpha.reviewer@example.com` · `multi.user@example.com` · password: `password`

## Technology

| Layer | Stack |
|-------|--------|
| Backend | Laravel 12, PHP 8.2+, Sanctum |
| Frontend | Vue 3, Vite, Pinia, Vue Router |
| AI | Provider abstraction — fake (offline) or Gemini when `GEMINI_API_KEY` is set |
| Evidence | JSON + PDF export (`mpdf`) |
| Academy | Organization-scoped courses and Community Safety lessons |
| ADAPT | First-party engine in `Adapt/` via HTTP integration |
| Database | SQLite (demo) / MySQL-capable |

## Testing

Verified baseline:

| Suite | Result |
|-------|--------|
| Backend | **170 tests passed** |
| Frontend | **42 tests passed** |
| Production build | **Success** |
| Synthetic evaluation | **PASS** — 42 scenarios, 0 critical failures |

```bash
cd backend && php artisan test
cd frontend && npm test
cd frontend && npm run build
cd backend && php artisan community-shield:evaluate
```

## Quick start

### Backend

```bash
cd backend
composer install
cp .env.example .env
php artisan key:generate
php artisan migrate --seed
php artisan serve
```

Optional: set `GEMINI_API_KEY` in `backend/.env` for live Gemini analysis. Reporting and review work without it (fake provider).

Optional: run ADAPT service and set `ADAPT_BASE_URL` for adaptive practice.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

| URL | Purpose |
|-----|---------|
| http://localhost:5173/welcome | Public landing page |
| http://localhost:5173/login | Sign in |

## Documentation

| Document | Purpose |
|----------|---------|
| [docs/GNCI_SUBMISSION.md](docs/GNCI_SUBMISSION.md) | Hackathon submission checklist |
| [docs/DEMO_RUNBOOK.md](docs/DEMO_RUNBOOK.md) | Written 3–5 minute demo |
| [docs/JUDGING.md](docs/JUDGING.md) | GNCI scorecard mapping |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture |
| [docs/DESIGN_SYSTEM.md](docs/DESIGN_SYSTEM.md) | Visual identity |
| [docs/SECURITY.md](docs/SECURITY.md) | Security boundaries |
| [docs/FINAL_READINESS.md](docs/FINAL_READINESS.md) | Readiness report |
| [docs/screenshots/README.md](docs/screenshots/README.md) | Screenshot capture guide |
| [docs/PHASE_1.md](docs/PHASE_1.md)–[docs/PHASE_11.md](docs/PHASE_11.md) | Phase history |

## Project boundaries

- `MSA Platform/` — pre-existing reference material (not modified)
- `Adapt/` — first-party ADAPT component
- Demo/seeded data is labeled — not production analytics
- Phase 12 was **not** started
- No claim of production scale, live platform integration, or measured real-world efficacy

## License

See repository license file.
