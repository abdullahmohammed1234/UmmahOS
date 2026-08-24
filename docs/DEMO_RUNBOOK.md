# UmmahOS Demo Runbook

**GNCI / judge demo — 3–5 minutes**  
**Start URL:** [http://localhost:5173/welcome](http://localhost:5173/welcome)

All data is **seeded and labeled**. Demo password: **`password`**

---

## Demo accounts

| Email | Organization | Role |
|-------|--------------|------|
| `alpha.member@example.com` | Demo MSA Alpha | Member |
| `alpha.reviewer@example.com` | Demo MSA Alpha | Community Safety Reviewer |
| `alpha.admin@example.com` | Demo MSA Alpha | Admin |
| `multi.user@example.com` | Alpha (reviewer) + Beta (admin) | Multi-org isolation demo |

---

## 0:00 — Open landing

1. Open `/welcome`
2. Read headline: *Community infrastructure for Muslim student organizations.*
3. Point to **AI assists. Humans decide.**
4. Scroll **The problem** — disconnected tools vs one system

**Say:** A community safety report should not end with a screenshot.

---

## 0:20 — Explain the problem

1. Show fragmented tools (forms, screenshots, spreadsheets, chats)
2. Scroll **UmmahOS loop** (Concern → … → ADAPT)
3. Show **screenshot vs structured context**
4. Show **Community Shield loop** (Report → Outcome)

---

## 0:40 — Community Shield

1. Click **Explore the Demo** → sign in as `alpha.member@example.com`
2. Confirm **Demo MSA Alpha** in organization switcher
3. Open **Community Shield**
4. Point to workflow: Capture → Context → Analyze → Review → Evidence → Outcome

---

## 1:10 — Structured context

1. Open **My Reports** → seeded report with context  
   **OR** start **Report a Concern** and walk through context sections
2. Highlight: original item, surrounding context, replies, related copies

**Say:** Context changes everything.

---

## 1:40 — Gemini / AI analysis

1. Sign out → sign in as `alpha.reviewer@example.com`
2. Open **Review Queue** → seeded report with analysis
3. Show **context relationship** diagram (actual recorded fields)
4. Show **AI Analysis** — advisory banner, signals, confidence, uncertainty

**Say:** Gemini assists. It does not decide. (Fake provider works offline if no API key.)

---

## 2:00 — Uncertainty

1. If high uncertainty banner is present, read it aloud
2. **Say:** Uncertainty is a valid outcome.

---

## 2:15 — Human review

1. Show **Human Review** panel — visually distinct from AI
2. Point to: Confirm · Mark Uncertain · Request Context · Escalate · Close
3. **Say:** Humans decide. No action is automatic.

---

## 2:40 — Evidence package

1. Scroll to **Evidence Package**
2. Expand sections: Incident, Context, AI, Uncertainty, Human Review, Outcome, Reporting Route, Safety & Privacy
3. Show **Export JSON** and **Export PDF**

**Say:** Exporting creates a report. It does not automatically submit it.

---

## 3:00 — What happened next?

1. Sign in as member (or show member view)
2. **My Reports** → report with outcomes
3. Timeline: Reported → Under Review → Decision → Outcome → Appeal / Correction

---

## 3:20 — Academy

1. **Academy** → **Community Safety**
2. Show Shield → Lesson → Scenario → ADAPT bridge
3. Open a seeded lesson linked to a confirmed pattern

---

## 3:40 — ADAPT

1. **Start Adaptive Practice**
2. Show Answer, Confidence, Reasoning
3. Submit → Feedback, What ADAPT noticed, Why this question?, Next challenge

---

## 4:00 — Multi-MSA isolation

1. Sign in as `multi.user@example.com`
2. Organization switcher lists Alpha (reviewer) and Beta (admin)
3. Switch **Demo MSA Alpha** → **Demo MSA Beta**
4. Show sidebar, permissions, announcements, and incidents change

**Say:** One platform. Many MSAs. Isolated data.

---

## 4:30 — Close

**Say:** Preserve context. Protect people. Track outcomes. Turn community learning into action. AI assists. Humans decide.

Optional: mention 170 backend tests, 42 frontend tests, 42 synthetic scenarios with 0 critical failures.

---

## Quick start (if demo is not running)

```bash
# Terminal 1
cd backend && composer install && cp .env.example .env && php artisan key:generate && php artisan migrate --seed && php artisan serve

# Terminal 2
cd frontend && npm install && npm run dev
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Empty review queue | `php artisan migrate --seed` |
| AI unavailable | Works offline with fake provider |
| ADAPT unavailable | Set `ADAPT_BASE_URL` or show unavailable message honestly |

## Do not claim

- AI accuracy percentages
- Seeded counts as real analytics
- Live platform enforcement
- Production deployment
