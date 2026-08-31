# Product Architecture

## 1. Core principle

One codebase, many isolated deployments. No `if customer_name == "x"`
branches anywhere in the code, no per-customer forks, no shared database
across customers. Everything a customer might want different from another
customer is either an **environment variable** (deployment-time, requires a
config change but not code) or a **`LibrarySettings` database field**
(admin-editable at runtime, no deployment involved at all).

## 2. What's core vs. configuration vs. per-deployment

| Layer | Lives in | Examples |
|---|---|---|
| Core product | The git repo | Models, views, business logic, templates, the design system |
| Deployment config | Environment variables (`.env`) | `SECRET_KEY`, `DATABASE_URL`, `ALLOWED_HOSTS`, SMTP credentials |
| Customer configuration | `LibrarySettings` (database, one row per deployment) | Organization name, branding colors, logo, loan policy, fines, feature toggles, contact/social info |
| Customer data | The customer's own database + media volume | Books, members, loans, fines |

Nothing customer-specific is ever committed to the repository. The only
"customer" data in the codebase is the demo data seeded by
`seed_demo_data`, which is clearly a development/demo tool, not something
a real deployment runs against live customer data.

## 3. Configuration system

`organization.models.LibrarySettings` is a singleton (`pk` is forced to
`1` on every save, and it can't be deleted - see the model's `save`/`delete`
overrides). `LibrarySettings.get_solo()` is the one way anything in the
app reads it. It's deliberately **not cached**: this is a one-row table, so
a plain query is cheap, and caching it correctly across multiple app-server
worker processes would need a shared cache backend this project doesn't
otherwise need, plus careful invalidation on every save - a stale-config
bug across workers after an admin changes settings would be a worse outcome
than one small extra query per request.

Every field on `LibrarySettings` is read by real code - there is no
configuration that toggles nothing (see `organization/access.py`,
`books/services.py`, `organization/views.py::branding_css`,
`organization/management/commands/send_due_reminders.py`). Fields for
functionality that doesn't exist yet (reservations, multi-branch, SMS/
WhatsApp) were deliberately **not** added - a flag with no behavior behind
it is worse than no flag.

## 4. Feature flags

`organization.features.is_enabled("enable_fines")` is the one entry point.
Flag names are exactly the boolean field names on `LibrarySettings` - no
separate registry to keep in sync. Enforcement is server-side via decorators
in `organization/access.py` (`@catalog_view`, `@member_portal_view`),
applied directly to the views they gate - not template conditionals that
merely hide a link. `organization/tests/test_access.py` proves this by
hitting the real URLs with the flag on and off.

## 5. Branding

`organization/views.py::branding_css` serves a tiny dynamically-generated
stylesheet (`/branding.css`) that overrides only the color custom
properties (`--color-primary`, `--gradient-brand`, etc.) already defined in
`students/static/students/css/tokens.css`. It's loaded after all the other
stylesheets in `base.html`. Because every component in the design system
(`components.css`) already consumes those variables instead of hardcoded
colors, changing a customer's brand colors in `/admin/` repaints buttons,
badges, the nav active state, and the auth-page gradient everywhere at
once - no component needs to know branding exists.

Logo/favicon are `ImageField`s on `LibrarySettings`; `students/context_processors.py`
exposes them (and address/hours/social links) to every template as
`LIBRARY_INFO`/`SOCIAL_LINKS`.

## 6. Roles and permissions

Uses Django's built-in `Group`/`Permission` system rather than a custom
role model - "boring, maintainable Django architecture" per the product
brief, and it's enforced by Django admin itself with zero extra code. A
`Librarians` group (seeded by a data migration,
`organization/migrations/0002_seed_librarian_group.py`) gets full CRUD on
the catalog/circulation models (`Book`, `Genre`, `Status`, `Loan`, `Fine`,
`Student`) but deliberately **not** on `User`, `Group`, `Permission`, or
`LibrarySettings` - organization/user administration stays superuser-only.
Add more groups the same way if a deployment needs finer-grained roles.

## 7. Deployment

`Dockerfile` + `docker-compose.production.yml` run the identical image for
every customer; only `.env` and the database differ. No Celery/Redis -
nothing in the app is asynchronous yet, so that infrastructure would be
pure overhead (see docs/deployment.md). `docker-entrypoint.sh` runs
migrations and `collectstatic` on every container start, so a deploy is
always on the latest schema without a separate manual step.

## 8. Extension strategy

A customer needing genuinely custom behavior should get it as an
**additional Django app** that hooks into the existing apps via their public
service functions (`books.services.borrow_book`/`return_book`,
`organization.features.is_enabled`) rather than edits scattered through the
core apps. None of the current codebase needed this yet, so no plugin
framework has been built speculatively - add one only when a second real
extension shows what the seam actually needs to look like.

## 9. What's deliberately not built yet, and why

- **Full i18n/RTL content.** `USE_I18N` is on and the architecture doesn't
  block adding `{% trans %}`/`gettext` wrapping later, but populating real
  Arabic translations needs native-speaker review this pass didn't have -
  shipping confidently-wrong translations would be worse than shipping none.
- **Barcode/QR scanning.** Needs real hardware/device testing to build
  responsibly; the checkout/return service functions
  (`borrow_book`/`return_book`) are already the right integration point
  once that workflow is designed.
- **Multi-branch / per-copy (`BookCopy`) inventory.** A real schema change
  touching the `Loan` model that was just carefully built with a
  uniqueness constraint on "one active loan per book" - deserves its own
  dedicated migration pass, not a bolt-on.
- **Custom fields on `Student`.** The configuration foundation
  (`LibrarySettings`, feature flags) this would build on now exists; the
  field-definition/validation system itself wasn't built this pass.
- **Audit logs.** Straightforward to add now that roles/permissions exist
  (log the same actions Django admin already gates) - a good next increment.
- **License/maintenance-expiry tracking.** `LibrarySettings` is the natural
  home for `license_type`/`maintenance_expiry_date` fields once needed; per
  the product brief, these should inform support/administration, never
  disable customer functionality.
- **Reservations.** No `Reservation` model or workflow exists in the app
  yet; adding the flag without the feature would be exactly the kind of
  meaningless configuration this pass avoided.

## 10. Verifying "no code changes per customer"

Everything a customer might ask for that's implemented so far - a
different loan period, fines on or off, a different brand color, the
public catalog members-only, the member portal disabled - is demonstrated
in `organization/tests/` purely by changing `LibrarySettings` fields and
observing different behavior from the same code and the same running
process. That's the acceptance test for "one codebase, many deployments":
no test needed to restart the server or edit a file to change how the app
behaves for a given customer.
