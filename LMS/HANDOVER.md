# Project Handover — LMS Library

This is a single, self-contained reference for picking up this project with
zero prior context. It covers what the project is, every app and model,
every setting and environment variable, the frontend design system, testing,
deployment, and known gaps. Two companion docs go deeper on specific topics:
`docs/architecture.md` (product/configuration architecture reasoning) and
`docs/deployment.md` (step-by-step deployment, backup, upgrade, troubleshooting).

---

## 1. What this is

A Django Library Management System, evolved in stages from a rough student
project into a maintainable, white-label-ready product:

1. **Backend hardening** — fixed real security bugs (broken access control,
   an ORM query that silently misclassified never-borrowed books as
   unavailable, a data-integrity bug in phone number storage), introduced a
   proper `Loan` model with history (replacing borrow-state-on-the-Book),
   cleaned up settings/URLs/migrations, added a test suite from zero.
2. **Frontend redesign** — replaced ad hoc per-page inline CSS with a real
   design-token system (light/dark/system theme), a component library
   (buttons, cards, forms, tables, badges, modals), and redesigned every
   page including auth flows.
3. **Commercial/white-label foundation** — a `LibrarySettings` singleton
   drives branding, loan policy, fines, and feature toggles per deployment;
   real server-side feature-flag enforcement; Docker + PostgreSQL
   deployment path; onboarding/reminder management commands.

The end state: **one codebase, deployed separately per customer**, each with
its own database and its own `LibrarySettings` row, no per-customer forks,
no shared multi-tenant database.

**User-facing scope**: students/members browse a book catalog, sign up,
borrow and return books, see their loan history and any fines, and manage
their profile. Cataloging, member/loan management, fines, and organization
configuration happen through Django admin (themed with django-jazzmin).
There is no separate custom-built staff dashboard.

---

## 2. Tech stack

| Layer | Choice |
|---|---|
| Framework | Django 5.0, Python 3.12 |
| Database | PostgreSQL in production (`psycopg[binary]`); SQLite by default in dev (zero setup) |
| Static files | WhiteNoise (no separate CDN/Nginx needed for static assets) |
| Admin theme | django-jazzmin |
| Frontend | Server-rendered Django templates, Bootstrap 5 grid utilities only (not Bootstrap's visual theme), a custom CSS design-token system, vanilla JS (no framework) |
| Task queue | **None** — no Celery/Redis. Nothing in the app is asynchronous yet; adding this infra now would be pure overhead. |
| Deployment | Docker (Dockerfile + docker-compose), or Render.com (`render.yaml`) |
| Linting/formatting | Ruff (`pyproject.toml`; `requirements-dev.txt`) |
| Testing | Django's built-in `TestCase` / `manage.py test` — no pytest, no separate test framework |

Full pinned dependency list: `requirements.txt` (11 packages, all actually
used — this was previously bloated with ~40 unrelated packages, since
cleaned up). Dev-only tooling: `requirements-dev.txt`.

**⚠️ Encoding landmine, already hit once**: `requirements.txt` was found
re-encoded as UTF-16LE (no BOM) mid-session by some external process/editor
(not this agent's own writes), which silently breaks `pip install -r
requirements.txt` with a cryptic "Invalid requirement" error. It's fixed as
of this handover (verified with a real `pip install --dry-run`), but if you
ever see that error again, run `file requirements.txt` — it must say
"ASCII text", not "data" or "UTF-16". If corrupted, rewrite it as plain
UTF-8 with the same 11 lines (see the file itself for the current list).

---

## 3. Repository layout

```
Library-Management-System-Website/        <- git repo root
├── .gitignore, .gitattributes            <- .gitattributes forces LF on *.sh/Dockerfile (Windows CRLF risk)
├── README.md                             <- user-facing project readme
└── LMS/                                  <- Django project root (manage.py lives here)
    ├── manage.py
    ├── requirements.txt, requirements-dev.txt
    ├── pyproject.toml                    <- Ruff config
    ├── .env.example                      <- copy to .env; see §5
    ├── VERSION                           <- plain version string, read by /healthz/
    ├── Dockerfile, docker-compose.yml, docker-compose.production.yml, docker-entrypoint.sh, .dockerignore
    ├── render.yaml                       <- alternative deployment target (Render.com)
    ├── docs/
    │   ├── architecture.md               <- product/config architecture reasoning
    │   ├── deployment.md                 <- deploy/backup/upgrade/troubleshoot
    │   └── customer-setup-checklist.md
    ├── LMS/                              <- settings package
    │   ├── settings.py, urls.py, wsgi.py, asgi.py
    ├── organization/                     <- deployment configuration app (§4.6)
    ├── books/                            <- catalog + borrow/return service layer (§4.2)
    ├── loans/                            <- Loan + Fine models (§4.3)
    ├── genre/, status/                   <- trivial lookup tables (§4.4, §4.5)
    ├── students/                         <- accounts, auth, profile, homepage (§4.1)
    ├── templates/                        <- project-level templates: error pages, shared includes
    ├── media/                            <- uploaded book covers etc. (gitignored; some demo images tracked in git history predate the ignore rule)
    └── staticfiles/                      <- collectstatic output (gitignored, regenerated)
```

---

## 4. Apps

### 4.1 `students` — accounts, auth, homepage

- **Models** (`students/models.py`): `Student` — `name`, `phone_number`
  (`CharField`, validated by `students/validators.py::phone_regex`;
  **historically an `IntegerField`, migrated deliberately** — see §7 for why
  that mattered), `email`, `birthdate`, `user` (`OneToOneField` to
  `auth.User`, nullable). No custom user model — plain `django.contrib.auth.User`.
- **Forms** (`students/forms.py`): `StyledFormMixin` injects the shared
  `.field-input` CSS class onto any form's widgets (used so built-in Django
  auth forms pick up the design system without a `django-widget-tweaks`
  dependency). `StudentCreationForm` (signup), `StudentEditForm` (profile
  edit), `StyledAuthenticationForm`/`StyledPasswordChangeForm`/
  `StyledPasswordResetForm`/`StyledSetPasswordForm` (styled wrappers around
  Django's built-in auth forms).
- **Views** (`students/views.py`): `index` (homepage — hero, best-sellers
  marquee, new releases, visit-us/follow-us sections), `profile` (a real
  personal dashboard: active/overdue loan counts, recent activity table),
  `StudentSignUp` (class-based, wraps User+Student creation in one
  transaction), `edit`. `profile` and `edit` are gated by
  `@organization.access.member_portal_view`.
- **`students/context_processors.py::library_info`** — injects
  `LIBRARY_INFO` and `SOCIAL_LINKS` into every template's context, sourced
  from the `LibrarySettings` singleton (not Django settings — see §4.6).
- **URLs** (`app_name = "students"`): `login`, `logout`, `profile`,
  `signup`, `<id>/edit/`. Password change/reset are **not** in this app's
  urls.py — see §4.6 note on why.
- **Templates**: `layouts/base.html` (the shell — see §6), `index.html`,
  `login.html`, `signup.html`, `logout.html`, `profile.html`, `edit.html`,
  and the six password-change/reset templates.

### 4.2 `books` — catalog, borrowing service layer

- **Models** (`books/models.py`): `Book` — `title`, `author`, `image`
  (falls back to `students/images/book-placeholder.svg` via
  `get_image_url()` if unset), `description`, `price`, `pages`, `status`
  (FK to `status.Status`, `on_delete=PROTECT`, default resolved by name via
  `get_default_status_id()` — **not a hardcoded PK**), `genre` (FK to
  `genre.Genre`), `created_at`. Note: **`Book.status` is largely vestigial**
  — availability is actually derived from `Loan`, not from `status` (see
  `is_available` property and §4.3). `status` still exists for admin
  filtering/display and future non-availability states (lost, damaged,
  etc.) but nothing currently sets it beyond the default.
  - `is_available` (property): `not self.loans.filter(returned_at__isnull=True).exists()`.
  - `active_loan` (property): the book's current active `Loan`, if any.
- **`books/services.py`** — **all borrow/return business logic lives here**,
  not in views or models:
  - `borrow_book(*, book, borrower, period_days)`: locks the `Book` row
    (`select_for_update`) inside a transaction, raises
    `BookNotAvailableError` if unavailable, raises `TooManyActiveLoansError`
    if the borrower is already at `LibrarySettings.max_books_per_member`,
    otherwise creates a `Loan`.
  - `return_book(*, loan)`: locks the `Loan` row, raises
    `LoanAlreadyReturnedError` if already returned, marks it returned, and
    — if `LibrarySettings.enable_fines` and the loan was overdue — creates a
    `Fine` capped at `LibrarySettings.maximum_fine`.
  - **Why locking matters**: this is the fix for a real race condition
    (two concurrent borrow requests for the same book) that existed in the
    original codebase.
- **`books/exceptions.py`**: `BookNotAvailableError`, `LoanAlreadyReturnedError`, `TooManyActiveLoansError`.
- **`books/forms.py`**: `BorrowForm` — `borrow_period` min=1, max dynamically
  computed as `max(LibrarySettings.loan_duration_days * 3, 30)` (so a
  customer with a long standard loan period, e.g. a semester loan, isn't
  blocked by a hardcoded ceiling), initial value defaults to the org's
  configured `loan_duration_days`.
- **Views** (`books/views.py`): `index` (search by title/author via `?q=`,
  filter by `?genre=<id>` and `?availability=available`, paginated 12/page
  — gated by `@organization.access.catalog_view`), `show` (detail page,
  also catalog-gated), `borrow` (`@login_required`), `show_borrowed` ("my
  loans", gated by `@member_portal_view`), `return_to_shelf`
  (`@login_required`, `@require_POST`, ownership-scoped via
  `get_object_or_404(Loan, book_id=id, borrower=request.user, returned_at__isnull=True)`).
- **⚠️ ORM gotcha already fixed once, don't reintroduce it**: never write
  `Book.objects.exclude(loans__returned_at__isnull=True)` to mean "books
  with no active loan" — Django translates that via a LEFT JOIN, and a book
  with **zero** loans at all also gets a NULL joined `returned_at`, so it
  gets wrongly excluded too (i.e. never-borrowed books would incorrectly
  show as unavailable). The correct pattern, used everywhere in this
  codebase: `Book.objects.exclude(id__in=Loan.objects.filter(returned_at__isnull=True).values("book_id"))`.
- **`books/management/commands/seed_demo_data.py`**: seeds 10 real books
  (using cover images already present in `media/books/images/` — legitimate
  published book covers, not placeholders) plus a realistic, clearly-demo
  spread of loan history (some returned, one active, one deliberately
  overdue) so search/filter/"most borrowed"/overdue badges all have real
  data on a fresh clone. Idempotent (`get_or_create` throughout).
- **Tests**: `books/tests/test_services.py` (borrow/return logic, max-loans
  enforcement, fine calculation, `BorrowForm` dynamic bounds),
  `books/tests/test_views.py` (access control, search/filter/pagination).

### 4.3 `loans` — loan history and fines

- **Models** (`loans/models.py`):
  - `Loan`: `book` (FK, `PROTECT`), `borrower` (FK to `AUTH_USER_MODEL`,
    `PROTECT`), `borrowed_at`, `due_at`, `returned_at` (null = active — the
    single source of truth for active/returned state; never duplicate this
    into a separate boolean). `Meta.constraints` has a **conditional unique
    constraint** — `UniqueConstraint(fields=["book"], condition=Q(returned_at__isnull=True))`
    — enforcing "no two active loans on the same book" at the database
    level, not just in application code. Properties: `is_active`,
    `is_overdue`, `days_overdue`, `loan_status` (`"Active"`/`"Overdue"`/`"Returned"`).
  - `Fine`: `loan` (`OneToOneField`, `PROTECT`), `amount`, `days_overdue`,
    `paid`. Only ever created by `books/services.py::return_book`.
- Both models use `on_delete=PROTECT` deliberately — deleting a `Book`,
  `User`, or `Loan` that has history/fines attached raises `ProtectedError`
  rather than silently cascading away financial/circulation records.
- **Tests**: `loans/tests.py` (model property correctness, the unique
  active-loan constraint).

### 4.4 `genre` / 4.5 `status` — lookup tables

Both are single-field (`name`, `unique=True`) lookup models managed
entirely through Django admin — no user-facing views or URLs beyond a
stub. Kept as separate apps rather than merged into `books`: moving a
model between Django apps safely requires coordinated
`SeparateDatabaseAndState` migrations, which was judged not worth the risk
for two trivial models (see `docs/architecture.md` §9 for the general
"don't build speculative complexity" reasoning that also applied here).

### 4.6 `organization` — deployment configuration (the white-label foundation)

This is the newest app and the one most worth understanding fully before
changing anything else in the product-architecture layer.

- **`organization/models.py::LibrarySettings`** — a **singleton** (every
  `save()` forces `pk=1`; `delete()` always raises `RuntimeError`).
  `LibrarySettings.get_solo()` is the *only* way anything reads it —
  **deliberately not cached** (a stale-config bug across multiple app-server
  worker processes after an admin edit would be worse than one extra cheap
  query per request; see the docstring in the model for the full reasoning
  — this was a real bug caught and fixed mid-build, not a design that was
  never tried).
  Fields, grouped by what actually consumes them:
  | Field | Consumed by |
  |---|---|
  | `organization_name`, `library_name`, `logo`, `favicon`, `support_email`, `support_phone`, `address`, `opening_hours`, `instagram_url`, `twitter_url`, `facebook_url` | `students/context_processors.py` → `LIBRARY_INFO`/`SOCIAL_LINKS` in every template |
  | `timezone` | Stored for display/future per-org TZ activation — **not yet wired into Django's active timezone per-request** (known gap, see §9) |
  | `primary_color`, `secondary_color`, `accent_color` | `organization/views.py::branding_css` (dynamic `/branding.css`) |
  | `default_theme_mode` | Stored; the actual light/dark/system *user* choice is client-side (localStorage, `students/static/students/js/theme.js`) — this field isn't yet read anywhere as an initial default (known gap, see §9) |
  | `loan_duration_days`, `max_books_per_member` | `books/services.py::borrow_book`, `books/forms.py::BorrowForm` |
  | `enable_fines`, `fine_per_day`, `maximum_fine` | `books/services.py::return_book` |
  | `enable_public_catalog` | `organization/access.py::catalog_view` |
  | `enable_member_portal` | `organization/access.py::member_portal_view` |
  | `enable_email_notifications` | `organization/management/commands/send_due_reminders.py` |

  **Rule to preserve**: every field must be read by real code. Do not add a
  `LibrarySettings` field "for later" — that was an explicit, repeated
  decision throughout this project (see `docs/architecture.md` §3, §9).

- **`organization/features.py`** — `features.is_enabled("enable_fines")`.
  Flag names are exactly the `LibrarySettings` boolean field names (no
  separate registry). Raises `ValueError` on an unknown flag name rather
  than silently returning `False`.
- **`organization/access.py`** — server-side enforcement decorators:
  - `@catalog_view`: allows anonymous access only while
    `enable_public_catalog` is on; falls back to `login_required` when off
    (the catalog becomes members-only, not taken down).
  - `@member_portal_view`: wraps `login_required`; when
    `enable_member_portal` is off, renders `organization/feature_disabled.html`
    with a 403 instead of the actual page.
  - These are applied directly to views (`books/views.py::index/show/show_borrowed`,
    `students/views.py::profile/edit`) — never rely on template-only hiding.
- **`organization/views.py`**:
  - `branding_css`: generates `/branding.css` on the fly, overriding only
    the color custom properties already defined in `tokens.css` (see §6).
    Includes `_darken`/`_tint` helpers (pure-Python hex color math, no
    dependency) for computing hover/soft color variants from the admin's
    single primary-color input.
  - `health_check`: `/healthz/` — `SELECT 1` against the DB, returns
    `{"status": "ok", "version": "..."}` (200) or `{"status": "error"}`
    (503). No auth, no internal detail exposed. Version comes from the
    plain-text `VERSION` file at the project root.
- **`organization/middleware.py::MaintenanceModeMiddleware`** — reads
  `settings.MAINTENANCE_MODE` (an **environment variable, not a
  `LibrarySettings` field** — it must keep working even if the database
  itself is down, e.g. mid-migration). Renders a fully standalone
  `organization/templates/organization/maintenance.html` (no `{% extends %}`,
  no DB-backed context processors — it must render even during a DB
  outage). Bypasses `/admin/` so staff can still get in. Placed early in
  `MIDDLEWARE`, before `SessionMiddleware`/`AuthenticationMiddleware`
  (which themselves touch the DB).
- **`organization/migrations/0002_seed_librarian_group.py`** — a data
  migration creating a **"Librarians" Django `Group`** with full
  view/add/change/delete permissions on `Book`, `Genre`, `Status`, `Loan`,
  `Fine`, `Student` — and **deliberately nothing** on `User`, `Group`,
  `Permission`, or `LibrarySettings` (organization/user administration
  stays superuser-only). This is real Django-admin-enforced role
  separation, not a custom role model — add more groups the same way if a
  deployment needs finer-grained roles.
- **Management commands**:
  - `setup_organization` — non-interactive onboarding (org name, branding,
    timezone, optional first admin user via `getpass` if no
    `--admin-password` given). Idempotent; safe to re-run.
  - `send_due_reminders` — emails members 2 days before a loan is due and 1
    day after it becomes overdue (fixed windows, not a tracked
    "already-notified" flag — see the module docstring for why). Meant to
    run daily via cron/scheduler; not automatic.
- **Tests**: `organization/tests/` — `test_models.py` (singleton behavior),
  `test_features.py`, `test_access.py` (integration tests hitting real URLs
  with flags on/off), `test_branding.py` (CSS output + color math),
  `test_reminders.py`, `test_setup_command.py`,
  `test_health_and_maintenance.py`.

---

## 5. Settings & environment variables

All settings live in `LMS/LMS/settings.py`, using `python-decouple`
(`config(...)`) for env vars and `dj-database-url` for the database — no
`base.py`/`development.py`/`production.py` split (judged unnecessary
indirection for a project this size).

| Variable | Default | Notes |
|---|---|---|
| `SECRET_KEY` | Django's insecure dev default | **Must** be a real random value in any deployed environment |
| `DEBUG` | `True` | Set `False` in production |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated |
| `MAINTENANCE_MODE` | `False` | See §4.6 |
| `DATABASE_URL` | `sqlite:///<BASE_DIR>/db.sqlite3` | Postgres in production: `postgres://user:pass@host:5432/db` |
| `EMAIL_BACKEND` | console backend if `DEBUG`, else SMTP | |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, `DEFAULT_FROM_EMAIL` | — | Only needed for real password-reset/reminder emails |

**Not environment variables** (deliberately, so a customer's own staff can
change them without a redeploy): organization name/branding/loan
policy/fines/feature toggles — all in `LibrarySettings` via `/admin/`.

`INSTALLED_APPS` order matters slightly: `organization` is registered
before `students`/`books`/etc. `MIDDLEWARE` order: `SecurityMiddleware` →
`WhiteNoiseMiddleware` → `MaintenanceModeMiddleware` → `SessionMiddleware`
→ ... (maintenance mode must run before anything DB-touching).

`TEMPLATES[0]['OPTIONS']['context_processors']` includes
`students.context_processors.library_info` — required globally for
`LIBRARY_INFO`/`SOCIAL_LINKS` to exist in any template, including the base
layout's navbar/footer.

Production security hardening (`SECURE_SSL_REDIRECT`,
`SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, HSTS) is gated behind
`if not DEBUG:` — see bottom of `settings.py`.

---

## 6. Frontend / design system

No CSS framework theme is used (Bootstrap is present only for its grid/JS
utilities, e.g. the mobile nav collapse — visual styling is 100% custom).

**CSS files** (`students/static/students/css/`, loaded in this order in
`base.html`):
1. `tokens.css` — all design tokens: color (light via `:root`, dark via
   both `prefers-color-scheme: dark` *and* `[data-theme="dark"]` so an
   explicit user choice always wins), spacing scale, radius scale, shadow
   scale, motion durations, typography scale, the one brand gradient.
2. `base.css` — resets, focus-visible rings (never removed without
   replacement), `prefers-reduced-motion` handling.
3. `layout.css` — header/nav shell, mobile nav drawer, page container.
4. `components.css` — buttons (primary/secondary/outline/ghost/danger,
   with a `.is-loading` spinner state), cards (default/elevated/interactive/
   highlighted/danger/stat), forms, tables, badges (status-semantic:
   success/warning/danger/info/neutral), alerts, pagination, empty states,
   filter/search bar, theme toggle, auth two-column shell, modal, marquee
   (best-sellers strip), hero (photo background + gradient scrim).
5. `/branding.css` (dynamic, not a static file — see §4.6) — overrides just
   the color tokens with the deployment's brand colors.

**Theme system**: an inline `<script>` at the very top of `base.html`'s
`<head>` (before any stylesheet) reads `localStorage['lms-theme']` and sets
`data-theme` on `<html>` synchronously — this prevents a flash of the wrong
theme. `students/static/students/js/theme.js` wires up the visible
light/dark/system toggle in the header. Respects OS `prefers-color-scheme`
when no explicit choice is stored.

**JS** (`students/static/students/js/`): `theme.js` (above),
`main.js` (mobile nav drawer, a reusable confirmation modal driven by
`<form data-confirm="...">` attributes — used for "return this book",
button loading-state on form submit). No framework, no build step.

**Shared template partials** (`templates/includes/`): `_navbar.html`,
`_messages.html` (Django messages rendered as styled alerts — this fixed a
real bug where flash messages were previously only visible on one page).

**Icons**: hand-rolled inline SVG (stroke-based, Lucide/Feather-style
aesthetic) — no icon font/library dependency.

**Known minor cruft**: `students/static/students/images/Editorial
commision.gif`, `Literature.gif`, `literature-script.svg` are leftover
unreferenced assets from the original project, never cleaned up. Safe to
delete if noticed, not urgent.

---

## 7. Database — full schema summary

All apps use `BigAutoField` PKs (`DEFAULT_AUTO_FIELD` in settings). Current
migration counts per app (all applied cleanly on a fresh DB and verified
against existing data during the original refactor):

| App | Migrations | Notable data migrations |
|---|---|---|
| `books` | 5 | `0002` backfills `Loan` rows from legacy borrow-state-on-Book (one-directional, `RunPython.noop` reverse) |
| `students` | 4 | `0002`-`0004`: expand/migrate/contract pattern for `phone_number` IntegerField→CharField (never do a direct `AlterField` type change on a column with real data — this pattern is the template to reuse) |
| `genre` | 3 | `0002` de-duplicates names before adding `unique=True` |
| `status` | 3 | same de-dup pattern as `genre` |
| `loans` | 2 | `0001` Loan, `0002` Fine |
| `organization` | 2 | `0001` LibrarySettings, `0002` seeds the Librarians group |

**Entity relationships**:
```
auth.User ──1:1── Student
auth.User ──1:N── Loan (borrower)         Book ──1:N── Loan (book, PROTECT)
Loan ──1:1── Fine (PROTECT)
Book ──N:1── Genre                        Book ──N:1── Status (PROTECT, default resolved by name)
```

`Loan` is the single source of truth for borrowing state — `Book` itself
carries no borrower/due-date fields (that was the original design flaw
fixed early in this project's history; see git log around "Loan model").

---

## 8. Testing

`python manage.py test` — 70 tests, all passing as of this handover, ~30s
runtime. No pytest, no fixtures files — tests build their own data in
`setUp()`. Structure: `tests/` packages (not single `tests.py`) in `books`,
`students`, `organization`; `loans/tests.py` is still a single file (small
enough not to need a package).

Run `ruff check . --fix && ruff format .` before committing — config is in
`pyproject.toml` (migrations are excluded from line-length checks since
they're auto-generated and shouldn't be hand-reformatted).

**Testing gotcha already hit once**: don't cache anything derived from
`LibrarySettings` across test methods — Django's `TestCase` rolls back the
DB transaction between tests but does **not** clear any application-level
cache, so a cached stale value from one test can leak into the next. This
is exactly why `LibrarySettings.get_solo()` has no caching at all (see §4.6).

---

## 9. Known gaps / deliberately deferred (with reasons)

From `docs/architecture.md` §9, reproduced here since it directly affects
what a next task might involve:

- **Full i18n/RTL content** — `USE_I18N=True` but no `{% trans %}` wrapping
  done yet; would need native-speaker translation review to do responsibly.
- **Barcode/QR scanning** — needs real hardware testing; integration point
  would be `books/services.py::borrow_book`/`return_book`.
- **Multi-branch / per-copy (`BookCopy`) inventory** — a real schema change
  touching `Loan`'s uniqueness constraint; deserves its own dedicated pass.
- **Custom fields on `Student`** — no field-definition/validation system
  built; `LibrarySettings`/feature-flag foundation it would sit on now exists.
- **Audit logs** — no model/logging exists yet; straightforward next
  increment now that roles/permissions exist.
- **License/maintenance-expiry tracking** — no fields exist on
  `LibrarySettings` yet; per the product brief, should inform
  support/administration only, never disable customer functionality.
- **Reservations** — no model/workflow exists at all.
- **`LibrarySettings.timezone` and `default_theme_mode`** — stored but not
  yet actively applied (per-request TZ activation via middleware; theme
  default consumed by `theme.js` on first visit before any localStorage
  value exists). Small, well-scoped follow-ups.
- **Docker/Postgres path** — reviewed carefully and internally consistent,
  but not live-verified in the environment this was built in (no running
  Docker daemon, no known local Postgres credentials at the time). Run a
  real `docker compose -f docker-compose.production.yml up --build` before
  relying on it for a real deployment.
- **Genre/availability search on the public catalog** exists (`books:index`
  view); there is no cross-field "smart search" beyond title/author
  `icontains` plus the two filters.

---

## 10. Getting started (local dev)

```bash
cd LMS
pip install -r requirements-dev.txt   # includes ruff
python manage.py migrate
python manage.py seed_demo_data       # optional: real books + demo loan history
python manage.py createsuperuser
python manage.py runserver
```

No `.env` needed for local dev — every setting has a working default
(SQLite, console email backend, insecure-but-functional `SECRET_KEY`).
Copy `.env.example` to `.env` only when you need to override something.

To exercise the Docker path locally: `docker compose up --build` (uses
`docker-compose.yml`, which runs Postgres + the Django dev server with live
reload).
