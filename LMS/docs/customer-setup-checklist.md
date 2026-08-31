# New Customer Setup Checklist

## Customer details
- [ ] Organization name
- [ ] Domain
- [ ] Logo (uploaded via Library settings once the admin account exists)
- [ ] Brand colors (primary / secondary / accent)
- [ ] Timezone
- [ ] Support email / phone / address / opening hours

## Infrastructure
- [ ] Server provisioned, Docker installed
- [ ] DNS pointed at the server
- [ ] Reverse proxy + TLS certificate in front of the app (see deployment.md §1)
- [ ] `.env` created from `.env.example` with a unique `SECRET_KEY` and
      `POSTGRES_PASSWORD`
- [ ] SMTP credentials configured (if password-reset emails and due-date
      reminders should actually send)
- [ ] Backup cron job scheduled (deployment.md §5)

## Configuration (`setup_organization`, then fine-tuned in `/admin/` > Library settings)
- [ ] Organization/library name, branding colors, timezone set
- [ ] Loan policy: `loan_duration_days`, `max_books_per_member`
- [ ] Fines: `enable_fines`, `fine_per_day`, `maximum_fine` (or leave disabled)
- [ ] Feature toggles: `enable_public_catalog`, `enable_member_portal`,
      `enable_email_notifications`
- [ ] First admin account created and password shared securely (not over
      plain email/chat)
- [ ] `Librarians` group used for any staff who shouldn't have full
      superuser/admin access

## Data migration
- [ ] Existing catalog imported (Django admin's built-in CSV-ish bulk entry,
      or a one-off script modeled on `books/management/commands/seed_demo_data.py`
      for anything larger)
- [ ] Existing members imported, if applicable

## Launch
- [ ] Staff walkthrough of Django admin (catalog, circulation, loans, fines)
- [ ] End-to-end acceptance test: browse catalog, sign up, borrow a book,
      return a book, confirm a fine is/isn't charged as configured
- [ ] `send_due_reminders` scheduled to run daily (deployment.md §10)
- [ ] `/healthz/` confirmed reachable and monitored
- [ ] Production launch
