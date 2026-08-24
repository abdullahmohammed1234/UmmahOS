# GNCI Hackathon — Submission Checklist

Use this document when completing the official GNCI submission form.

> **No video** — the repository must communicate the project on its own.

## Project link

| Item | Value |
|------|--------|
| Repository | [https://github.com/abdullahmohammed1234/UmmahOS](https://github.com/abdullahmohammed1234/UmmahOS) |
| Local demo | See [README](../README.md#quick-start) |
| Written demo | [DEMO_RUNBOOK.md](DEMO_RUNBOOK.md) |

## Short project description (suggested text)

UmmahOS is community infrastructure for Muslim student organizations. It replaces screenshot-only safety reporting with structured context, advisory Gemini analysis, human review, evidence packages, outcome tracking, and a bridge to Academy lessons and ADAPT adaptive practice. AI assists; humans decide. Multiple MSAs share one platform with strict tenant isolation.

## Team information

Fill in before submitting:

| Field | Your entry |
|-------|------------|
| Team name | _[Team name]_ |
| Member 1 — name | _[Full name]_ |
| Member 1 — participant agreement email | _[Email used on agreement]_ |
| Member 2 — name | _[Full name]_ |
| Member 2 — participant agreement email | _[Email]_ |
| _(add rows as needed)_ | |

## Reviewer instructions

1. Open the repository README — it contains the full product story, architecture links, and demo accounts.
2. Clone the repo and follow **Quick start** in README (about 5 minutes).
3. Visit `/welcome` for the product narrative.
4. Follow [DEMO_RUNBOOK.md](DEMO_RUNBOOK.md) for a 3–5 minute walkthrough.
5. Optional deep dives: [JUDGING.md](JUDGING.md), [ARCHITECTURE.md](ARCHITECTURE.md), [SECURITY.md](SECURITY.md).

**Demo password:** `password` (all seeded accounts)

## Key demo accounts

| Email | Organization | Role |
|-------|--------------|------|
| `alpha.member@example.com` | Demo MSA Alpha | Member |
| `alpha.reviewer@example.com` | Demo MSA Alpha | Community Safety Reviewer |
| `multi.user@example.com` | Alpha + Beta | Reviewer (Alpha) · Admin (Beta) |

## Screenshots

Capture per [screenshots/README.md](screenshots/README.md) and commit to `docs/screenshots/` before final submission so README embeds render.

## What we do not claim

- Production deployment or user counts
- Real-world AI accuracy or harm-reduction efficacy
- Live integration with social platforms
- Automatic content removal or enforcement

## Verification commands (for reviewers)

```bash
cd backend && php artisan test
cd frontend && npm test && npm run build
cd backend && php artisan community-shield:evaluate
```

Expected: 170 backend tests, 42 frontend tests, synthetic evaluation PASS (42 scenarios, 0 critical failures).
