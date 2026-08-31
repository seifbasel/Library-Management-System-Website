"""Send due-soon and overdue email reminders. Intended to run once daily
(cron, a scheduled task, etc.) - see docs/deployment.md.

To avoid re-notifying the same loan every day without adding a tracking
field, each loan is only ever contacted at two fixed points: exactly 2 days
before it's due, and exactly 1 day after it becomes overdue.
"""

from datetime import timedelta

from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone

from loans.models import Loan
from organization import features
from organization.models import LibrarySettings

DUE_SOON_DAYS_BEFORE = 2
OVERDUE_DAYS_AFTER = 1


class Command(BaseCommand):
    help = "Email members whose loans are due soon or just became overdue."

    def handle(self, *args, **options):
        if not features.is_enabled("enable_email_notifications"):
            self.stdout.write("Email notifications are disabled for this deployment - nothing sent.")
            return

        settings_obj = LibrarySettings.get_solo()
        today = timezone.localdate()
        sent = 0

        due_soon = Loan.objects.filter(
            returned_at__isnull=True, due_at=today + timedelta(days=DUE_SOON_DAYS_BEFORE)
        ).select_related("book", "borrower")
        for loan in due_soon:
            sent += self._notify(loan, settings_obj, subject_prefix="Due soon", days_phrase="in 2 days")

        overdue = Loan.objects.filter(
            returned_at__isnull=True, due_at=today - timedelta(days=OVERDUE_DAYS_AFTER)
        ).select_related("book", "borrower")
        for loan in overdue:
            sent += self._notify(loan, settings_obj, subject_prefix="Overdue", days_phrase="yesterday")

        self.stdout.write(self.style.SUCCESS(f"Sent {sent} reminder email(s)."))

    def _notify(self, loan, settings_obj, *, subject_prefix, days_phrase):
        if not loan.borrower.email:
            return 0
        send_mail(
            subject=f"{subject_prefix}: {loan.book.title}",
            message=(
                f"Hi {loan.borrower.get_username()},\n\n"
                f'"{loan.book.title}" was due {days_phrase} ({loan.due_at}).\n'
                f"Please return it to {settings_obj.library_name} at your earliest convenience.\n\n"
                f"Thanks,\n{settings_obj.library_name}"
            ),
            from_email=None,  # uses DEFAULT_FROM_EMAIL
            recipient_list=[loan.borrower.email],
            fail_silently=False,
        )
        return 1
