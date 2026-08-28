"""Business logic for borrowing and returning books.

Kept out of views/models so the borrow/return rules - availability
checks, the race-condition guard, and the resulting state transition -
live in exactly one place.
"""

from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from books.exceptions import BookNotAvailableError, LoanAlreadyReturnedError
from books.models import Book
from loans.models import Loan


def borrow_book(*, book: Book, borrower, period_days: int) -> Loan:
    """Create a Loan for `book`, or raise if it's already borrowed.

    Locks the Book row for the duration of the transaction so two
    concurrent borrow requests for the same book can't both succeed.
    """
    with transaction.atomic():
        locked_book = Book.objects.select_for_update().get(pk=book.pk)
        if not locked_book.is_available:
            raise BookNotAvailableError(f"'{locked_book.title}' is not currently available.")

        borrowed_at = timezone.localdate()
        due_at = borrowed_at + timedelta(days=period_days)
        return Loan.objects.create(
            book=locked_book,
            borrower=borrower,
            borrowed_at=borrowed_at,
            due_at=due_at,
        )


def return_book(*, loan: Loan) -> Loan:
    """Mark `loan` as returned, or raise if it already was."""
    with transaction.atomic():
        locked_loan = Loan.objects.select_for_update().get(pk=loan.pk)
        if not locked_loan.is_active:
            raise LoanAlreadyReturnedError(f"The loan for '{locked_loan.book}' has already been returned.")

        locked_loan.returned_at = timezone.localdate()
        locked_loan.save(update_fields=["returned_at", "updated_at"])
        return locked_loan
