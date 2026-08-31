from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from books.exceptions import BookNotAvailableError, LoanAlreadyReturnedError, TooManyActiveLoansError
from books.forms import BorrowForm
from books.models import Book
from books.services import borrow_book, return_book
from loans.models import Fine
from organization.models import LibrarySettings


class BorrowBookServiceTests(TestCase):
    def setUp(self):
        self.borrower = User.objects.create_user("reader", password="pass12345")
        self.book = Book.objects.create(title="Test Book", author="Author", price="9.99")

    def test_borrow_book_creates_active_loan_and_makes_book_unavailable(self):
        self.assertTrue(self.book.is_available)
        loan = borrow_book(book=self.book, borrower=self.borrower, period_days=7)
        self.assertTrue(loan.is_active)
        self.assertFalse(Book.objects.get(pk=self.book.pk).is_available)

    def test_borrow_book_rejects_already_borrowed_book(self):
        borrow_book(book=self.book, borrower=self.borrower, period_days=7)
        other_borrower = User.objects.create_user("reader2", password="pass12345")
        with self.assertRaises(BookNotAvailableError):
            borrow_book(book=self.book, borrower=other_borrower, period_days=7)

    def test_return_book_marks_loan_returned_and_book_available_again(self):
        loan = borrow_book(book=self.book, borrower=self.borrower, period_days=7)
        returned_loan = return_book(loan=loan)
        self.assertFalse(returned_loan.is_active)
        self.assertTrue(Book.objects.get(pk=self.book.pk).is_available)

    def test_return_book_rejects_double_return(self):
        loan = borrow_book(book=self.book, borrower=self.borrower, period_days=7)
        return_book(loan=loan)
        with self.assertRaises(LoanAlreadyReturnedError):
            return_book(loan=loan)

    def test_borrow_book_rejects_once_borrower_hits_max_books_per_member(self):
        settings_obj = LibrarySettings.get_solo()
        settings_obj.max_books_per_member = 1
        settings_obj.save()

        borrow_book(book=self.book, borrower=self.borrower, period_days=7)
        second_book = Book.objects.create(title="Second Book", author="Author", price="9.99")

        with self.assertRaises(TooManyActiveLoansError):
            borrow_book(book=second_book, borrower=self.borrower, period_days=7)

    def test_returning_a_book_frees_up_a_loan_slot(self):
        settings_obj = LibrarySettings.get_solo()
        settings_obj.max_books_per_member = 1
        settings_obj.save()

        loan = borrow_book(book=self.book, borrower=self.borrower, period_days=7)
        return_book(loan=loan)

        second_book = Book.objects.create(title="Second Book", author="Author", price="9.99")
        borrow_book(book=second_book, borrower=self.borrower, period_days=7)  # should not raise

    def test_no_fine_when_fines_disabled(self):
        settings_obj = LibrarySettings.get_solo()
        settings_obj.enable_fines = False
        settings_obj.save()

        loan = borrow_book(book=self.book, borrower=self.borrower, period_days=7)
        loan.due_at = timezone.localdate() - timedelta(days=10)  # force it overdue
        loan.save()
        returned_loan = return_book(loan=loan)

        self.assertFalse(hasattr(returned_loan, "fine"))

    def test_fine_assessed_and_capped_when_returned_late(self):
        settings_obj = LibrarySettings.get_solo()
        settings_obj.enable_fines = True
        settings_obj.fine_per_day = "1.00"
        settings_obj.maximum_fine = "5.00"
        settings_obj.save()

        loan = borrow_book(book=self.book, borrower=self.borrower, period_days=7)
        # 10 days overdue, at $1/day that's $10 - above the $5 cap
        loan.due_at = timezone.localdate() - timedelta(days=10)
        loan.save()

        returned_loan = return_book(loan=loan)

        self.assertTrue(Fine.objects.filter(loan=returned_loan).exists())
        fine = returned_loan.fine
        self.assertEqual(fine.days_overdue, 10)
        self.assertEqual(fine.amount, Decimal("5.00"))  # capped, not the $10 that 10 days would otherwise cost


class BorrowFormTests(TestCase):
    def setUp(self):
        settings_obj = LibrarySettings.get_solo()
        settings_obj.loan_duration_days = 14
        settings_obj.save()

    def test_accepts_the_configured_default_period(self):
        form = BorrowForm(data={"borrow_period": 14})
        self.assertTrue(form.is_valid(), form.errors)

    def test_rejects_zero_or_negative(self):
        self.assertFalse(BorrowForm(data={"borrow_period": 0}).is_valid())
        self.assertFalse(BorrowForm(data={"borrow_period": -5}).is_valid())

    def test_rejects_far_beyond_the_dynamic_ceiling(self):
        self.assertFalse(BorrowForm(data={"borrow_period": 10_000}).is_valid())

    def test_rejects_non_numeric_period(self):
        self.assertFalse(BorrowForm(data={"borrow_period": "not-a-number"}).is_valid())

    def test_ceiling_scales_with_the_configured_default(self):
        # default=14 -> ceiling is 14*3=42, so 100 should be rejected...
        self.assertFalse(BorrowForm(data={"borrow_period": 100}).is_valid())

        # ...but once the org's default period is raised (e.g. a semester
        # loan policy), the same value becomes acceptable.
        settings_obj = LibrarySettings.get_solo()
        settings_obj.loan_duration_days = 60
        settings_obj.save()
        self.assertTrue(BorrowForm(data={"borrow_period": 100}).is_valid())
