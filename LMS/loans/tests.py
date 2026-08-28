from datetime import timedelta

from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from books.models import Book
from loans.models import Loan


class LoanModelTests(TestCase):
    def setUp(self):
        self.borrower = User.objects.create_user("reader", password="pass12345")
        self.book = Book.objects.create(title="Test Book", author="Author", price="9.99")

    def _make_loan(self, *, borrowed_days_ago=0, due_in_days=14, returned=False):
        borrowed_at = timezone.localdate() - timedelta(days=borrowed_days_ago)
        return Loan.objects.create(
            book=self.book,
            borrower=self.borrower,
            borrowed_at=borrowed_at,
            due_at=borrowed_at + timedelta(days=due_in_days),
            returned_at=timezone.localdate() if returned else None,
        )

    def test_active_loan_is_active_and_not_overdue(self):
        loan = self._make_loan(due_in_days=14)
        self.assertTrue(loan.is_active)
        self.assertFalse(loan.is_overdue)
        self.assertEqual(loan.loan_status, "Active")
        self.assertEqual(loan.days_overdue, 0)

    def test_active_loan_past_due_date_is_overdue(self):
        loan = self._make_loan(borrowed_days_ago=20, due_in_days=10)
        self.assertTrue(loan.is_active)
        self.assertTrue(loan.is_overdue)
        self.assertEqual(loan.loan_status, "Overdue")
        self.assertEqual(loan.days_overdue, 10)

    def test_returned_loan_is_never_overdue_even_if_due_date_passed(self):
        loan = self._make_loan(borrowed_days_ago=20, due_in_days=10, returned=True)
        self.assertFalse(loan.is_active)
        self.assertFalse(loan.is_overdue)
        self.assertEqual(loan.loan_status, "Returned")
        self.assertEqual(loan.days_overdue, 0)

    def test_cannot_create_two_active_loans_for_the_same_book(self):
        self._make_loan()
        other_borrower = User.objects.create_user("reader2", password="pass12345")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Loan.objects.create(
                    book=self.book,
                    borrower=other_borrower,
                    borrowed_at=timezone.localdate(),
                    due_at=timezone.localdate() + timedelta(days=14),
                )

    def test_a_second_loan_is_allowed_once_the_first_is_returned(self):
        first = self._make_loan()
        first.returned_at = timezone.localdate()
        first.save()

        second = self._make_loan()  # should not raise
        self.assertTrue(second.is_active)
