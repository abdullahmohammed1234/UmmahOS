# Phase 9 — Academy + ADAPT Integration

Phase 9 connects **Community Shield** validated patterns to **UmmahOS Academy** education and the external **ADAPT** adaptive-learning engine.

## Objective

Community Shield protects the community today; Academy + ADAPT helps members become better prepared for similar situations tomorrow — without turning incident data into learner surveillance.

## Product principle

```text
Incident → Human review → Abstracted LearningPattern → Academy → ADAPT
```

**Not:**

```text
Incident → AI → Automatically create lesson
```

Community Shield incidents are **not** directly exposed to learners. Phase 9 uses human-created, sanitized learning patterns as the bridge between safety reporting and education.

ADAPT remains an adaptive-learning engine. It does **not** classify learners as safe/unsafe or hateful/non-hateful.

## Architecture

```text
Community Shield (confirmed incident)
        ↓
Human-created LearningPattern (draft → approved)
        ↓
LearningRecommendation (published)
        ↓
Academy Lesson + Scenarios
        ↓
AdaptChallengeAdapter → AdaptClient (HTTP)
        ↓
ADAPT engine (strategy + next challenge)
```

UmmahOS does **not** rebuild ADAPT. The integration boundary is:

| Component | Role |
|-----------|------|
| `AdaptChallengeAdapter` | Maps Academy scenario fields to ADAPT session start parameters |
| `AdaptClient` | Interface for create session / submit response |
| `HttpAdaptClient` | Production/demo client → `ADAPT_BASE_URL` (default `http://127.0.0.1:8765`) |
| `FakeAdaptClient` | Deterministic client for Laravel tests only |

## LearningPattern

Sanitized educational abstraction. Creators enter title, summary, learning objective, pattern type, and domain. The system **never** auto-copies reporter identity, reviewer notes, raw evidence, or incident text.

| Field | Notes |
|-------|-------|
| `source_incident_id` | Internal provenance for staff only |
| `pattern_type` | Controlled taxonomy (`contextual_hate`, `coded_language`, …) |
| `status` | `draft` → `approved` → `archived` |

Only **confirmed** incidents (`review_outcome = confirmed`) may be promoted.

## LearningRecommendation

Links an approved pattern to Academy course/lesson with a human-written reason. Status: `draft` | `published` | `archived`. Only approved patterns may receive **published** recommendations.

## Academy extension

Reuses existing `Course`. Adds:

- `academy_lessons` (category `community_safety`)
- `academy_scenarios` (mapped to ADAPT challenge IDs)
- `academy_lesson_progress` (`started` / `completed`)
- `adapt_learning_sessions` (local ownership pointer; ADAPT owns learner state)

## RBAC

| Permission | Admin | Reviewer | Member |
|------------|-------|----------|--------|
| `education.patterns.view` | ✓ | ✓ | ✗ |
| `education.patterns.create` | ✓ | ✓ | ✗ |
| `education.patterns.manage` | ✓ | ✗ | ✗ |
| `education.recommendations.manage` | ✓ | ✗ | ✗ |
| Academy published content (`courses.view`) | ✓ | ✓* | ✓ |

\*Reviewers do not receive unrestricted Academy administration (`courses.manage`).

## Learner privacy

- Members never receive `source_incident_id` on recommendation payloads.
- ADAPT sessions are owned by the starting user (IDOR blocked).
- Reviewers do not automatically receive learner performance data.
- No learner safety labels; no person→education targeting.

## Multi-MSA isolation

All education records are `organization_id`-scoped. Alpha patterns/lessons/recommendations never appear in Beta.

## Demo content

**Alpha** (`alpha.member@example.com` / `password`):

1. Confirmed Reddit incident (existing Phase 7/8 seed)
2. Approved LearningPattern: *Contextual Religious Targeting*
3. Published recommendation → lesson *Understanding Context Before Responding*
4. Five demo ADAPT scenarios (`CSAFE-CTX-001`…`005`)

**Beta**: separate *Beta Community Safety* lesson for isolation demos.

Scenarios are labeled **Demo / educational scenario**.

## Running ADAPT (real engine)

From the ADAPT repository (sibling checkout, gitignored as `Adapt/` like `MSA Platform/`):

```bash
python -m app
# listens on 127.0.0.1:8765
```

Community Safety domain challenges live in ADAPT’s catalog (`community-safety` / `csafety-context`). Set in UmmahOS backend `.env`:

```env
ADAPT_BASE_URL=http://127.0.0.1:8765
```

If ADAPT is down, Academy lessons still work and show: *Adaptive practice is temporarily unavailable.*

## API (organization-scoped)

| Method | Path |
|--------|------|
| GET/POST | `/community-shield/reports/{report}/learning-pattern` |
| PATCH | `/learning-patterns/{pattern}` |
| POST | `/learning-patterns/{pattern}/approve` |
| GET/POST | `/learning-recommendations` |
| GET | `/academy/community-safety` |
| GET | `/academy/lessons/{lesson}` |
| POST | `/academy/lessons/{lesson}/adapt-sessions` |
| POST | `/academy/adapt-sessions/{session}/responses` |

## Demo flows

**Member:** Academy → Community Safety → Understanding Context → Start Adaptive Practice → answer + confidence + reasoning → What ADAPT noticed → Why this question? → next challenge from ADAPT.

**Reviewer:** Review Queue → confirmed incident → Education → Create Learning Pattern (draft).

**Admin:** Learning Patterns → Approve → Create recommendation → attach lesson.

## Limitations

- Academy remains a thin LMS (lessons + scenarios + minimal progress), not a full curriculum platform.
- ADAPT challenges are curated catalog items (not generated at runtime).
- Phase 9 does not auto-generate lessons from Gemini or incidents.
- No cross-MSA pattern intelligence, learner risk scoring, or analytics dashboards (Phase 10+).
- Human learning efficacy is not claimed.

## Tests

Backend feature coverage in `Phase9EducationTest` (patterns, approval, recommendations, isolation, adapter, session ownership, unavailable mode). Frontend Vitest coverage in `phase9Education.spec.ts`.

## Out of scope (not started)

Phase 10 items: advanced analytics, organization-wide safety dashboards, cross-MSA intelligence, automated educational generation, automated learner risk scoring, platform API integrations, automated moderation, notifications, ML retraining, public safety dashboards.
