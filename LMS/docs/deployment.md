# Deployment Guide

This app is designed as **one reusable codebase, deployed separately per
customer** - each customer gets their own container, their own PostgreSQL
database, and their own configuration. There is no shared multi-tenant
database and no per-customer code fork: everything that differs between
customers lives in environment variables and the `LibrarySettings` row in
that customer's own database.

## 1. What you need per customer

- A server (VPS, or any host that can run Docker) reachable at the
  customer's domain.
- A PostgreSQL database (the `docker-compose.production.yml` file provisions
  one automatically; a managed Postgres instance works too - just point
  `DATABASE_URL` at it).
- A domain, with DNS pointed at the server.
- A TLS certificate. This project does not run its own reverse proxy or
  certificate automation - put a reverse proxy in front (Caddy is the
  simplest: it gets Let's Encrypt certs automatically; Nginx + certbot also
  works) that forwards to the app container's port 8000 and sets
  `X-Forwarded-Proto: https`. `SECURE_PROXY_SSL_HEADER` in `settings.py`
  already expects that header once `DEBUG=False`.
- (Optional) real SMTP credentials, if you want the password-reset flow to
  send actual emails instead of doing nothing useful in the void.

## 2. New installation, step by step

```bash
# 1. Get the code onto the server
git clone <repo-url> library
cd library/LMS

# 2. Configure environment variables
cp .env.example .env
# Edit .env: SECRET_KEY (generate a real one - see the comment in the file),
# DEBUG=False, ALLOWED_HOSTS=customer-domain.com, POSTGRES_PASSWORD, and
# email settings if you want password-reset emails to actually send.

# 3. Build and start
docker compose -f docker-compose.production.yml up -d --build
# The entrypoint runs migrations and collectstatic automatically on every
# start - see docker-entrypoint.sh.

# 4. One-time organization setup: branding, loan policy, and the first
# admin account. Safe to re-run if you need to change any of it later.
docker compose -f docker-compose.production.yml exec web \
  python manage.py setup_organization \
  --organization-name "Riverside School" \
  --library-name "Riverside Library" \
  --primary-color "#1F6F4A" \
  --timezone "America/Chicago" \
  --admin-username admin --admin-email admin@riverside.example \
  --admin-password "change-me-immediately"

# 5. (Optional) seed real books, or your own catalog import
docker compose -f docker-compose.production.yml exec web \
  python manage.py seed_demo_data
```

Then log in to `/admin/` with the admin account and fine-tune the rest
under **Library settings** - fines, member limits, feature toggles, social
links, contact info. None of that requires touching code or redeploying.

## 3. Environment variables

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Django's cryptographic signing key. Generate a real one per deployment - never share it across customers. |
| `DEBUG` | `False` in every real deployment. |
| `ALLOWED_HOSTS` | Comma-separated list; must include the customer's real domain. |
| `DATABASE_URL` | `postgres://user:password@host:5432/dbname`. |
| `POSTGRES_PASSWORD` (docker-compose.production.yml only) | Initializes the bundled Postgres container; must match the password in `DATABASE_URL`. |
| `MAINTENANCE_MODE` | `True` to take the site down for all non-admin traffic without touching the database (works even mid-migration). |
| `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, `DEFAULT_FROM_EMAIL` | SMTP for password resets and due-date reminders. Omit for local/demo use - emails print to the console instead. |

Organization identity, branding colors, loan policy, fines, and feature
toggles are **not** environment variables - they live in the database
(`LibrarySettings`, editable in `/admin/`) so a customer's own staff can
change them without redeploying.

## 4. Database

Production always uses PostgreSQL. Local development defaults to SQLite
(zero setup) unless `DATABASE_URL` is set - see `docker-compose.yml` for a
local Postgres instance if you want to test against the same engine as
production before deploying.

## 5. Backups

`docker-compose.production.yml` mounts `./backups` into the `db` container.
A simple daily dump:

```bash
docker compose -f docker-compose.production.yml exec -T db \
  pg_dump -U lms lms | gzip > backups/lms-$(date +%F).sql.gz

# keep the last 30 days, delete anything older
find backups -name '*.sql.gz' -mtime +30 -delete
```

Put that in a daily cron job on the host. Also back up the `media_data`
volume (uploaded book covers and logos) with the same retention policy -
`docker run --rm -v library_media_data:/data -v $(pwd)/backups:/backup
alpine tar czf /backup/media-$(date +%F).tar.gz /data`.

**Restore:**

```bash
gunzip -c backups/lms-2026-08-01.sql.gz | \
  docker compose -f docker-compose.production.yml exec -T db psql -U lms lms
```

Restore media the same way in reverse (extract the tar into the volume).

## 6. Upgrading to a new version

```bash
git pull
docker compose -f docker-compose.production.yml exec -T db \
  pg_dump -U lms lms | gzip > backups/pre-upgrade-$(date +%F).sql.gz   # always back up first
docker compose -f docker-compose.production.yml up -d --build
# migrations + collectstatic run automatically via docker-entrypoint.sh
docker compose -f docker-compose.production.yml exec web \
  curl -f http://localhost:8000/healthz/ || echo "check logs before declaring success"
```

**Rollback**, if something goes wrong: `git checkout <previous-tag>`, then
`docker compose -f docker-compose.production.yml up -d --build` again. If a
migration in the new version needs reverting too, restore the pre-upgrade
backup rather than trying to hand-write a reverse migration under pressure.

## 7. Health checks

`GET /healthz/` returns `{"status": "ok", "version": "1.0.0"}` (200) when
the app can reach its database, or `{"status": "error"}` (503) otherwise.
No authentication, no internal detail exposed - safe to point an uptime
monitor or load balancer at it directly. Both `docker-compose.yml` and
`docker-compose.production.yml` already use it as the `web` service's
Docker healthcheck.

## 8. Maintenance mode

Set `MAINTENANCE_MODE=True` in `.env` and restart the `web` service to show
a plain "temporarily unavailable" page to everyone except `/admin/`. Works
even if the database itself is down (it's an environment variable, not a
database setting) - use it while running a risky migration or restoring
from backup.

## 9. Troubleshooting

- **Container won't start / "no such file or directory" on `docker-entrypoint.sh`**:
  usually a CRLF line-ending issue if the repo was checked out on Windows
  without `.gitattributes` being respected. Run `git config core.autocrlf`
  and confirm `.gitattributes` (repo root) is present before building.
- **500 errors immediately after deploy**: check `SECRET_KEY` and
  `ALLOWED_HOSTS` are set correctly in `.env`; check `docker compose logs web`.
- **CSRF failures on form submission behind the reverse proxy**: confirm
  your proxy sets `X-Forwarded-Proto: https` and that `ALLOWED_HOSTS`
  includes the exact domain being used.
- **Password reset emails never arrive**: with no `EMAIL_HOST` configured,
  emails print to the container's stdout instead of sending - check
  `docker compose logs web` and then configure real SMTP credentials.

## 10. Scheduled tasks

Due-date reminder emails aren't automatic - run this once daily (cron, a
scheduled task on the host, or your platform's scheduler):

```bash
docker compose -f docker-compose.production.yml exec web python manage.py send_due_reminders
```

It's a no-op if `enable_email_notifications` is off for that deployment, or
if no loan falls in the notification window that day.
