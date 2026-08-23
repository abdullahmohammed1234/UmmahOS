# UmmahOS Backend

Phase 1 backend for **UmmahOS** — digital infrastructure for Muslim Student Associations.

This is a new Laravel 12 API. It is not the SFU MSA Platform application.

## Stack

- PHP 8.2+
- Laravel 12
- Laravel Sanctum
- SQLite for local development (configurable)

## Setup

```bash
composer install
copy .env.example .env
php artisan key:generate
php artisan migrate --seed
php artisan serve
```

Demo password for seeded users: `password`

- `alpha.admin@example.com` — Demo MSA Alpha admin
- `alpha.member@example.com` — Demo MSA Alpha member
- `alpha.reviewer@example.com` — Demo MSA Alpha Community Safety Reviewer
- `beta.admin@example.com` — Demo MSA Beta admin
- `beta.reviewer@example.com` — Demo MSA Beta Community Safety Reviewer
- `multi.user@example.com` — Alpha Community Safety Reviewer + Beta admin
- `outsider@example.com` — no memberships

## Tests

```bash
php artisan test
```

Laravel is licensed under the MIT license.
