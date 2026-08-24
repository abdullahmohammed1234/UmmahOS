# Recommended screenshots for GNCI submission

Capture these **locally** after setup. **Do not fabricate images.**

```bash
cd backend && php artisan migrate --seed
cd frontend && npm run dev
# Backend: php artisan serve
```

Save files to this folder (`docs/screenshots/`). Once captured, they render in [README](../README.md#screenshots).

## Required captures

| File | Page / state | What must be visible |
|------|--------------|----------------------|
| `01-landing.png` | `/welcome` | Hero headline, **AI assists. Humans decide.**, Explore the Demo CTA |
| `02-community-shield.png` | `/community-shield` (Alpha member) | Community Shield landing, workflow steps |
| `03-context.png` | Review detail OR report wizard step 4 | Context relationship view or structured context fields |
| `04-ai-analysis.png` | `/community-shield/review-queue/:id` | AI Analysis panel, advisory banner, uncertainty |
| `05-human-review.png` | Same review detail | Human Review panel, action buttons |
| `06-evidence-package.png` | Review detail — Evidence Package | Sections + Export JSON/PDF + export disclaimer |
| `07-outcome.png` | `/community-shield/my-reports/:id` | **What happened next?** timeline |
| `08-academy-adapt.png` | Community Safety lesson + ADAPT session | Shield → Lesson bridge; ADAPT feedback |
| `09-multi-msa.png` | App shell as `multi.user@example.com` | Org switcher showing Alpha + Beta roles |

## Accounts

| Email | Password | Use for |
|-------|----------|---------|
| `alpha.member@example.com` | `password` | 02, 07 |
| `alpha.reviewer@example.com` | `password` | 03–06 |
| `multi.user@example.com` | `password` | 09 |

## Capture tips

- Desktop width ~1280px for README grid
- Keep **Demo MSA Alpha** (or current org) visible in app screenshots
- Use seeded data only — no fake metrics
- One mobile frame of `/welcome` is optional
- PNG format, descriptive filenames exactly as listed above

## After capture

```bash
git add docs/screenshots/*.png
git commit -m "Add GNCI submission screenshots"
git push
```

Verify images render in README before submitting the repository link.
