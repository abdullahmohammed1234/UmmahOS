# Judge Scorecard Mapping

This document maps UmmahOS implementation to the hackathon scorecard criteria. **No score is claimed** — this explains how the product addresses each criterion.

> **AI assists. Humans decide.**

---

## Impact — 25%

**Demonstrate:** Real MSA/community reporting problem, fragmented workflows, context loss, need for trained human review, measurable outcome tracking.

| Evidence | Where to see it |
|----------|-----------------|
| Problem statement | Landing page `/welcome` — "The problem" section |
| Context loss vs structured evidence | Landing page before/after Community Shield section |
| Member reporting flow | `/community-shield` — structured wizard with platform, visibility, context, replies |
| Human review requirement | Review queue disclaimer, AI advisory banners |
| Outcome tracking | `/community-shield/my-reports/:id` — "What happened next?" timeline |
| Multi-org reality | Organization switcher in app sidebar |

**Demo path:** Landing → Member report → My Reports detail

---

## Functionality — 25%

**Demonstrate:** Incident → Context → AI → Human Review → Evidence → Outcome

| Step | Implementation |
|------|----------------|
| Incident | Community Shield report wizard (7 sections) |
| Context | Original item, surrounding context, replies, related copies, language |
| AI | Review detail `/community-shield/review-queue/:id` — AI Context Analysis card |
| Human Review | Review actions: confirm, uncertain, escalate, request context |
| Evidence | Evidence package with preview, JSON export, PDF export |
| Outcome | OutcomeTrackingPanel — external reports, verification, appeals |

**Demo path:** Review queue → Review detail → Evidence export → Outcome panel

---

## Innovation — 15%

**Demonstrate:** Context-preserving evidence, cross-platform incident model, human-centered AI, Academy bridge, ADAPT adaptive learning.

| Innovation | Evidence |
|------------|----------|
| Context-preserving evidence | Report wizard completeness indicator; evidence package sections |
| Cross-platform model | Platform options: X, YouTube, TikTok, Reddit, Discord, Telegram, WhatsApp |
| Human-centered AI | Advisory disclaimer, uncertainty surfacing, no auto-enforcement |
| Academy bridge | Learning patterns from confirmed incidents → Community Safety courses |
| ADAPT | `/academy/adapt-sessions/:id` — adaptive loop with "What ADAPT noticed" |

**Demo path:** Seeded report with context → AI analysis → Academy lesson → ADAPT challenge

---

## Ethics — 15%

**Demonstrate:** Human oversight, uncertainty, privacy boundaries, synthetic evaluation, no automatic enforcement, tenant isolation.

| Principle | Implementation |
|-----------|----------------|
| Human oversight | Human Review block visually distinct from AI block |
| Uncertainty allowed | High uncertainty banner; "Mark Uncertain" reviewer action |
| Privacy boundaries | Reporter notes hidden from members; internal notes not in member view |
| Synthetic evaluation | Phase 10: 42 scenarios, 0 critical failures (`docs/PHASE_10.md`) |
| No auto-enforcement | Export disclaimer: packages are informational, not auto-submitted |
| Tenant isolation | Organization switcher demo; cross-org access denied in tests |

**Demo path:** Show uncertainty in AI analysis → Human decision → Ethics section on landing page

---

## Sustainability — 10%

**Demonstrate:** Multi-MSA architecture, organization-scoped RBAC, reusable platform infrastructure.

| Aspect | Evidence |
|--------|----------|
| Multi-MSA | Seeded orgs: Demo MSA Alpha, Beta, Gamma, Delta |
| RBAC | Role-aware sidebar: member vs reviewer vs admin sections |
| Tenant isolation | `organizationStore` tests; switching org reloads context |
| Modular architecture | Community Shield, Academy, ADAPT as distinct modules |
| Reusable infrastructure | Central design system, shared UI components |

**Demo path:** Switch organization in sidebar → Show permission changes

---

## Communication — 10%

**Demonstrate:** Polished landing page, before/after story, clear product flow, focused demo, clear terminology.

| Asset | Location |
|-------|----------|
| Landing page | `/welcome` |
| Product story workflow | Landing page "From concern to learning" |
| Before/after | Community Shield landing section |
| Demo runbook | `docs/DEMO_RUNBOOK.md` |
| Design system | `docs/DESIGN_SYSTEM.md` |
| Consistent terminology | "AI assists. Humans decide." throughout product |

**Demo path:** Start at landing page, follow `DEMO_RUNBOOK.md`

---

## Key differentiators to highlight

1. **Structured evidence** — Not just screenshots
2. **AI advisory boundary** — Visually obvious in reviewer UI
3. **What happened next?** — Outcome tracking timeline
4. **Academy → ADAPT loop** — Learning from confirmed patterns
5. **Organization switcher** — Quiet proof of multi-MSA architecture
