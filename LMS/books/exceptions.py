class BookNotAvailableError(Exception):
    """Raised when trying to borrow a book that already has an active loan."""


class LoanAlreadyReturnedError(Exception):
    """Raised when trying to return a loan that has already been returned."""


class TooManyActiveLoansError(Exception):
    """Raised when a borrower is already at LibrarySettings.max_books_per_member."""
