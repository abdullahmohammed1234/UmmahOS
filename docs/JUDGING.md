# GNCI Judge Scorecard Mapping

Maps **implemented** UmmahOS behavior to the GNCI hackathon scorecard. **No score is claimed.**

> **AI assists. Humans decide.**  
> A community safety report should not end with a screenshot.

| Criterion | Weight |
|-----------|--------|
| Impact | 25% |
| Functionality | 25% |
| Innovation | 15% |
| Ethics | 15% |
| Sustainability | 10% |
| Communication | 10% |

---

## Impact — 25%

**What we demonstrate:** MSAs lose context when safety workflows live in forms, screenshots, spreadsheets, and chats. UmmahOS unifies reporting, review, evidence, outcomes, and learning in one organization-aware system.

| | |
|---|---|
| **Where it exists** | `/welcome` problem section; Community Shield report wizard; My Reports |
| **What the judge should look at** | Before/after context comparison; seeded Alpha incident with replies and related items |
| **Repository evidence** | `frontend/src/pages/LandingPage.vue`, `CommunityShieldPage.vue`, `DemoCommunitySeeder.php` |

**Demo path:** Landing → Member report or My Reports

---

## Functionality — 25%

**What we demonstrate:** End-to-end workflow: Incident → Context → AI → Human Review → Evidence → Outcome

| Step | Route / component |
|------|-------------------|
| Incident | `/community-shield` report wizard |
| Context | Original item, surrounding context, replies, related copies |
| AI | `/community-shield/review-queue/:id` — AI Analysis |
| Human Review | Confirm, Mark Uncertain, Request Context, Escalate, Close |
| Evidence | Evidence Package preview, JSON/PDF export |
| Outcome | Outcome Tracking — What happened next? |

| | |
|---|---|
| **Repository evidence** | Backend feature tests in `tests/Feature/Community/`; frontend `humanReview.spec.ts`, `evidencePackage.spec.ts`, `outcomeTracking.spec.ts` |

**Demo path:** Review queue → Review detail → Evidence → Outcome panel

---

## Innovation — 15%

**What we demonstrate:** Context-preserving evidence model; cross-platform incident capture; human-centered advisory AI; safety-to-education bridge; ADAPT adaptive practice.

| Innovation | Judge should look at |
|------------|---------------------|
| Context preservation | Context relationship view; report completeness indicator |
| Cross-platform model | X, YouTube, TikTok, Reddit, Discord, Telegram, WhatsApp, Other |
| Human-centered AI | Advisory vs authoritative UI distinction; uncertainty banners |
| Academy bridge | Learning Pattern from confirmed review → Community Safety lesson |
| ADAPT | `/academy/adapt-sessions/:id` — What ADAPT noticed / Why this question? |

| | |
|---|---|
| **Repository evidence** | `ContextRelationshipView.vue`, `IncidentEvidencePackageService.php`, `Phase9EducationTest.php` |

---

## Ethics — 15%

**What we demonstrate:** Human oversight, explicit uncertainty, privacy boundaries, no automatic enforcement, synthetic safety evaluation, tenant isolation.

| Principle | Implementation |
|-----------|----------------|
| Human oversight | Human Review visually distinct from AI Analysis |
| Uncertainty allowed | High uncertainty banner; Mark Uncertain action |
| Privacy | Member views omit internal notes; learner payloads omit source incident IDs |
| No auto-enforcement | Evidence export disclaimer |
| Synthetic evaluation | 42 scenarios, 7 categories, 0 critical failures |
| Tenant isolation | Organization-scoped queries; IDOR tests |

| | |
|---|---|
| **Repository evidence** | `docs/SECURITY.md`, `CommunityShieldEvaluationRunnerTest.php`, `IncidentEvidencePackageTest.php` |

---

## Sustainability — 10%

**What we demonstrate:** Multi-MSA infrastructure reusable across organizations; RBAC; modular Community Shield + Academy + ADAPT.

| | |
|---|---|
| **Where** | Organization switcher; seeded Alpha/Beta/Gamma/Delta |
| **Judge should look at** | `multi.user@example.com` — reviewer in Alpha, admin in Beta |
| **Repository evidence** | `OrganizationContextTest.php`, `TenantIsolationTest.php`, `OrganizationSwitcher.vue` |

---

## Communication — 10%

**What we demonstrate:** Repository communicates without video — README, landing page, demo runbook, architecture, screenshots guide, scorecard mapping.

| Asset | Location |
|-------|----------|
| Product README | `README.md` |
| GNCI checklist | `docs/GNCI_SUBMISSION.md` |
| Demo runbook | `docs/DEMO_RUNBOOK.md` |
| Architecture | `docs/ARCHITECTURE.md` |
| Screenshots guide | `docs/screenshots/README.md` |
| Landing page | `/welcome` |

---

## Claims we do not make

- Production user counts or real-world harm reduction
- AI accuracy percentages on live content
- Automatic takedowns or platform integration
- That seeded demo data represents live analytics
