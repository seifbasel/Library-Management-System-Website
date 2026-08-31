from datetime import timedelta
from io import StringIO

from django.contrib.auth.models import User
from django.core import mail
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from books.models import Book
from loans.models import Loan
from organization.models import LibrarySettings


class SendDueRemindersTests(TestCase):
    def setUp(self):
        self.borrower = User.objects.create_user("reader", email="reader@example.com", password="pass12345")
        self.book = Book.objects.create(title="Reminder Book", author="Author", price="9.99")
        self.today = timezone.localdate()

    def _make_loan(self, due_at, book=None):
        return Loan.objects.create(
            book=book or self.book,
            borrower=self.borrower,
            borrowed_at=self.today - timedelta(days=10),
            due_at=due_at,
        )

    def test_sends_due_soon_reminder_exactly_two_days_before(self):
        self._make_loan(due_at=self.today + timedelta(days=2))
        call_command("send_due_reminders", stdout=StringIO())

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Due soon", mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].to, ["reader@example.com"])

    def test_sends_overdue_reminder_exactly_one_day_after(self):
        self._make_loan(due_at=self.today - timedelta(days=1))
        call_command("send_due_reminders", stdout=StringIO())

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Overdue", mail.outbox[0].subject)

    def test_no_reminder_outside_the_two_notification_windows(self):
        other_book = Book.objects.create(title="Another Book", author="Author", price="9.99")
        self._make_loan(due_at=self.today + timedelta(days=5))
        self._make_loan(due_at=self.today - timedelta(days=5), book=other_book)
        call_command("send_due_reminders", stdout=StringIO())

        self.assertEqual(len(mail.outbox), 0)

    def test_no_reminder_for_a_returned_loan(self):
        loan = self._make_loan(due_at=self.today + timedelta(days=2))
        loan.returned_at = self.today
        loan.save()
        call_command("send_due_reminders", stdout=StringIO())

        self.assertEqual(len(mail.outbox), 0)

    def test_nothing_sent_when_email_notifications_disabled(self):
        settings_obj = LibrarySettings.get_solo()
        settings_obj.enable_email_notifications = False
        settings_obj.save()

        self._make_loan(due_at=self.today + timedelta(days=2))
        call_command("send_due_reminders", stdout=StringIO())

        self.assertEqual(len(mail.outbox), 0)

    def test_skips_borrower_with_no_email_on_file(self):
        self.borrower.email = ""
        self.borrower.save()
        self._make_loan(due_at=self.today + timedelta(days=2))
        call_command("send_due_reminders", stdout=StringIO())

        self.assertEqual(len(mail.outbox), 0)
