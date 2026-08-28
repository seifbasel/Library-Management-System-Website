from django.contrib.auth.models import User
from django.test import TestCase

from books.exceptions import BookNotAvailableError, LoanAlreadyReturnedError
from books.forms import BorrowForm
from books.models import Book
from books.services import borrow_book, return_book


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


class BorrowFormTests(TestCase):
    def test_accepts_period_within_range(self):
        form = BorrowForm(data={"borrow_period": 1})
        self.assertTrue(form.is_valid())
        form = BorrowForm(data={"borrow_period": 30})
        self.assertTrue(form.is_valid())

    def test_rejects_period_out_of_range(self):
        self.assertFalse(BorrowForm(data={"borrow_period": 0}).is_valid())
        self.assertFalse(BorrowForm(data={"borrow_period": 31}).is_valid())
        self.assertFalse(BorrowForm(data={"borrow_period": -5}).is_valid())

    def test_rejects_non_numeric_period(self):
        self.assertFalse(BorrowForm(data={"borrow_period": "not-a-number"}).is_valid())
