# Online Library Management System

> **Picking this project up (human or AI agent)?** Read
> [`LMS/HANDOVER.md`](LMS/HANDOVER.md) first — a complete technical
> reference: every app/model, all settings and environment variables,
> the frontend design system, testing, deployment, and known gaps.

## Project Overview

This is a web-based library management system built with Django. It lets students browse a book catalog, borrow and return books, and manage their profile, while librarians manage the catalog and view loan activity through Django's admin site.

## Features

### Admin (Django Admin, themed with Jazzmin)

- View, add, edit, and delete books, genres, statuses, and student profiles
- View all loans (current and historical) with borrower, dates, and status
- Manage user accounts and permissions via Django's built-in admin

There is no separate custom-built admin dashboard app - all administrative work happens through Django's admin site at `/admin/`.

### Student Module

- **Registration & Authentication**
  - Self-service signup with phone number, birthdate, and email validation
  - Login / logout
  - Password change and password reset (emailed link)

- **Browse Books**
  - Search by title/author, filter by genre and availability, paginated
  - View detailed information for any book

- **Borrow & Return**
  - Borrow an available book for a chosen number of days (1-30)
  - View your currently borrowed books, with due dates and overdue status
  - Return a borrowed book to the shelf

- **Profile**
  - A personal dashboard: active/overdue loan counts, recent activity
  - Edit your name, phone number, email, and birthdate

Per-deployment organization name, branding colors, loan policy, and fines
are configurable in Django admin under **Library settings** - no code
changes or redeploy needed. See `LMS/HANDOVER.md` for the full picture.

## Known Limitations

- No reservations system - a student can't reserve a book that's currently out.
- No staff-facing dashboard page (stats, recent activity) beyond Django admin and the student-facing profile page.
- No i18n/RTL, barcode scanning, multi-branch inventory, or custom fields yet - see `LMS/HANDOVER.md` §9 for the full list and reasoning.

## Technologies Used

- **Backend:** Django 5.0
- **Database:** SQLite by default (zero setup for local development); PostgreSQL in production via `DATABASE_URL`
- **Frontend:** HTML, CSS, Bootstrap 5
- **Authentication:** Django's built-in authentication system
- **Admin theme:** django-jazzmin
- **Static files:** WhiteNoise

## Installation Guide

### Prerequisites

1. Python 3.10+
2. pip (Python package manager)

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone [repository-url]
   cd Library-Management-System-Website/LMS
   ```

2. **Create and Activate a Virtual Environment**
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # Linux/Mac
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   Copy `.env.example` to `.env` and adjust as needed. With no `.env` at all, the
   project still runs out of the box using a local SQLite database:
   ```bash
   cp .env.example .env
   ```

5. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a Superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the Development Server**
   ```bash
   python manage.py runserver
   ```

8. **Access the Application**
   - Main site: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

To use PostgreSQL instead of SQLite, set `DATABASE_URL` in `.env` (see the
commented example in `.env.example`) before running migrations.

## Usage

### Admin Access
1. Log in to the admin panel using your superuser credentials
2. Manage books, genres, statuses, students, and loans
3. Review current and past loan activity

### Student Access
1. Register a new account
2. Log in with your credentials
3. Browse and borrow books
4. View and return your borrowed books, and manage your profile

## Running Tests

```bash
python manage.py test
```

## Project Structure
```
LMS/
├── books/              # Book catalog, borrow/return service layer
├── loans/              # Loan history (borrow records, overdue tracking)
├── students/           # Student accounts, auth, profile
├── genre/              # Genre lookup
├── status/             # Book status lookup
├── media/              # Uploaded book cover images (not committed to git)
├── static/             # Project-level static assets
├── templates/          # Shared templates (includes, error pages)
└── LMS/                # Django project settings, root urlconf
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Django Documentation
- Bootstrap Documentation
- Jazzmin Theme Contributors
