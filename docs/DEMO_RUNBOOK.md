# UmmahOS Demo Runbook

**Target duration:** 3–5 minutes  
**Start URL:** [http://localhost:5173/welcome](http://localhost:5173/welcome)

All demo data is **seeded and labeled**. Demo password for all accounts: **`password`**

---

## Demo accounts

| Email | Organization | Role |
|-------|--------------|------|
| `alpha.member@example.com` | Demo MSA Alpha | Member |
| `alpha.reviewer@example.com` | Demo MSA Alpha | Community Safety Reviewer |
| `alpha.admin@example.com` | Demo MSA Alpha | Admin |
| `multi.user@example.com` | Alpha (reviewer) + Beta (admin) | Multi-org demo |

---

## 0:00–0:30 — Landing page

1. Open `/welcome`
2. Read headline: *"Build stronger, safer Muslim student communities"*
3. Point to **AI assists. Humans decide.**
4. Scroll to **"From concern to learning"** workflow
5. Show Community Shield **before/after** (screenshot vs structured evidence)
6. Click **Open Demo** → sign in

**Say:** MSAs manage operations and safety across disconnected tools. UmmahOS unifies them with organization-aware isolation.

---

## 0:30–1:15 — Member: Community Shield

1. Sign in as `alpha.member@example.com`
2. Confirm organization: **Demo MSA Alpha** (sidebar org switcher)
3. Navigate: **Community Shield**
4. Show landing: workflow Capture → Review → Respond → Follow Up
5. Click **Report a Concern** OR open **My Reports** → seeded report
6. If submitting: fill platform, content type, visibility, description, optional context

**Say:** Members preserve context — not just screenshots. More context helps trained reviewers.

---

## 1:15–2:00 — Reviewer: Evidence + AI + Human decision

1. Sign out → sign in as `alpha.reviewer@example.com`
2. Navigate: **Review Queue**
3. Open a seeded report (e.g. report with context and AI analysis)
4. Walk through evidence sections: Incident → Original Item → Context → Replies
5. Show **AI Context Analysis** — note advisory banner
6. If high uncertainty: point to uncertainty banner
7. Show **Human Review** block — visually distinct from AI
8. Demonstrate human action (confirm / mark uncertain) if appropriate

**Say:** AI identifies signals and uncertainty. Trained reviewers decide independently.

---

## 2:00–2:30 — Evidence package

1. On review detail, scroll to evidence package section
2. Show **Preview**, **Export JSON**, **Export PDF**
3. Note: exports are informational — **not automatically submitted to platforms**

**Say:** Professional case file for documentation and external reporting routes.

---

## 2:30–3:00 — Outcome: "What happened next?"

1. Sign in as member OR show member view
2. Navigate: **My Reports** → open report with outcomes
3. Show timeline: Report recorded → Under review → Human decision → Outcome

**Say:** We don't stop at "report submitted." Members see reporter-visible updates.

---

## 3:00–3:45 — Education: Academy + ADAPT

1. Navigate: **Academy** → **Community Safety**
2. Open a lesson linked to a confirmed community pattern
3. Start **ADAPT** practice session
4. Show adaptive loop: Your response → What ADAPT noticed → Feedback → Next challenge

**Say:** Confirmed patterns become education. ADAPT adapts based on learner evidence.

---

## 3:45–4:15 — Architecture (optional if time)

1. Sign in as `multi.user@example.com`
2. Use **organization switcher** → switch Alpha ↔ Beta
3. Show sidebar permissions change (reviewer vs admin sections)
4. Mention: 170 backend tests, 42 synthetic safety scenarios, 0 critical failures

**Say:** One platform, multiple MSAs, strict tenant isolation.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Backend not running | `cd backend && php artisan serve` |
| Frontend not running | `cd frontend && npm run dev` |
| ADAPT unavailable | Check backend ADAPT integration env vars |
| AI analysis fails | Fake provider works offline; Gemini requires API key |
| Empty review queue | Run `php artisan migrate --seed` |

---

## What NOT to demo

- Do not claim AI accuracy percentages
- Do not present seeded counts as real analytics
- Do not bypass authorization with fake shortcuts
- Do not modify `MSA Platform/` reference material

---

## Quick command reference

```bash
# Terminal 1 — Backend
cd backend && php artisan serve

# Terminal 2 — Frontend
cd frontend && npm run dev

# Verify tests
cd backend && php artisan test
cd frontend && npm test && npm run build
```
