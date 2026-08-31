"""Business logic for borrowing and returning books.

Kept out of views/models so the borrow/return rules - availability
checks, the race-condition guard, the borrow-limit and fine policy, and
the resulting state transitions - live in exactly one place.
"""

from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from books.exceptions import BookNotAvailableError, LoanAlreadyReturnedError, TooManyActiveLoansError
from books.models import Book
from loans.models import Fine, Loan
from organization import features
from organization.models import LibrarySettings


def borrow_book(*, book: Book, borrower, period_days: int) -> Loan:
    """Create a Loan for `book`, or raise if it's unavailable or the
    borrower is already at their active-loan limit.

    Locks the Book row for the duration of the transaction so two
    concurrent borrow requests for the same book can't both succeed.
    """
    with transaction.atomic():
        locked_book = Book.objects.select_for_update().get(pk=book.pk)
        if not locked_book.is_available:
            raise BookNotAvailableError(f"'{locked_book.title}' is not currently available.")

        settings_obj = LibrarySettings.get_solo()
        active_loan_count = Loan.objects.filter(borrower=borrower, returned_at__isnull=True).count()
        if active_loan_count >= settings_obj.max_books_per_member:
            raise TooManyActiveLoansError(
                f"You already have {active_loan_count} active loan(s), "
                f"the maximum allowed is {settings_obj.max_books_per_member}."
            )

        borrowed_at = timezone.localdate()
        due_at = borrowed_at + timedelta(days=period_days)
        return Loan.objects.create(
            book=locked_book,
            borrower=borrower,
            borrowed_at=borrowed_at,
            due_at=due_at,
        )


def return_book(*, loan: Loan) -> Loan:
    """Mark `loan` as returned, or raise if it already was.

    If fines are enabled and the book came back late, assesses a Fine
    based on how many days overdue it was, capped at the deployment's
    configured maximum.
    """
    with transaction.atomic():
        locked_loan = Loan.objects.select_for_update().get(pk=loan.pk)
        if not locked_loan.is_active:
            raise LoanAlreadyReturnedError(f"The loan for '{locked_loan.book}' has already been returned.")

        today = timezone.localdate()
        days_overdue = max((today - locked_loan.due_at).days, 0)

        locked_loan.returned_at = today
        locked_loan.save(update_fields=["returned_at", "updated_at"])

        if days_overdue and features.is_enabled("enable_fines"):
            settings_obj = LibrarySettings.get_solo()
            amount = min(settings_obj.fine_per_day * days_overdue, settings_obj.maximum_fine)
            Fine.objects.create(loan=locked_loan, amount=amount, days_overdue=days_overdue)

        return locked_loan
