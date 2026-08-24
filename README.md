# UmmahOS

**Community infrastructure for Muslim student organizations.**

UmmahOS brings MSA operations, community safety, evidence-based review, and adaptive education into one organization-aware platform.

> **AI assists. Humans decide.**

## What is UmmahOS?

Muslim Student Associations manage members, events, resources, education, and community safety across disconnected tools. UmmahOS unifies these workflows with strict multi-organization tenant isolation.

### Core capabilities

| Feature | Description |
|---------|-------------|
| **Community operations** | Announcements, events, resources, members |
| **Community Shield** | Context-preserving incident reporting with structured evidence |
| **Human-centered AI** | Advisory AI analysis for trained reviewers — not automatic enforcement |
| **Outcome tracking** | "What happened next?" — external reports, decisions, appeals |
| **Academy** | Organization-scoped courses and Community Safety learning |
| **ADAPT** | Adaptive practice that responds to learner evidence |

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

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit:

- **Landing page:** [http://localhost:5173/welcome](http://localhost:5173/welcome)
- **Sign in:** [http://localhost:5173/login](http://localhost:5173/login)

### Demo credentials

Seeded demo password for all demo users: **`password`**

See [docs/DEMO_RUNBOOK.md](docs/DEMO_RUNBOOK.md) for the recommended judge demo flow and account list.

## Documentation

| Document | Purpose |
|----------|---------|
| [docs/PHASE_11.md](docs/PHASE_11.md) | Phase 11 product polish summary |
| [docs/DESIGN_SYSTEM.md](docs/DESIGN_SYSTEM.md) | Visual identity and design tokens |
| [docs/JUDGING.md](docs/JUDGING.md) | Scorecard mapping for judges |
| [docs/DEMO_RUNBOOK.md](docs/DEMO_RUNBOOK.md) | 3–5 minute demo script |
| [docs/PHASE_1.md](docs/PHASE_1.md) – [docs/PHASE_10.md](docs/PHASE_10.md) | Phase implementation history |

## Architecture highlights

- **Multi-MSA:** One platform, multiple organizations, strict tenant isolation
- **RBAC:** Organization-scoped roles and permissions
- **Community Shield:** Incident → Context → AI → Human Review → Evidence → Outcome → Learning
- **Synthetic evaluation:** 42 safety scenarios, 0 critical failures (Phase 10)

## Tests

```bash
# Backend (from backend/)
php artisan test

# Frontend (from frontend/)
npm test

# Production build
npm run build
```

## Important boundaries

- `MSA Platform/` is pre-existing reference material — **do not modify**
- ADAPT lives in `Adapt/` as a first-party component
- Demo/seeded data is clearly labeled — not presented as production analytics
- Phase 12 was **not** started

## License

See repository license file.
