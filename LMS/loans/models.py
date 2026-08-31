from django.conf import settings
from django.db import models
from django.utils import timezone


class Loan(models.Model):
    """A single borrow event for a physical book.

    A loan is "active" while ``returned_at`` is null; that field is the
    single source of truth for active/returned state, so it is never
    duplicated into a separate boolean flag that could drift out of sync.
    """

    book = models.ForeignKey(
        "books.Book",
        on_delete=models.PROTECT,
        related_name="loans",
    )
    borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="loans",
    )
    borrowed_at = models.DateField()
    due_at = models.DateField()
    returned_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["book"],
                condition=models.Q(returned_at__isnull=True),
                name="unique_active_loan_per_book",
            ),
        ]
        indexes = [
            models.Index(fields=["book", "returned_at"]),
            models.Index(fields=["borrower", "returned_at"]),
            models.Index(fields=["due_at"]),
        ]

    def __str__(self):
        return f"{self.book} borrowed by {self.borrower}"

    @property
    def is_active(self):
        return self.returned_at is None

    @property
    def is_overdue(self):
        return self.is_active and self.due_at < timezone.localdate()

    @property
    def days_overdue(self):
        if not self.is_overdue:
            return 0
        return (timezone.localdate() - self.due_at).days

    @property
    def loan_status(self):
        if not self.is_active:
            return "Returned"
        if self.is_overdue:
            return "Overdue"
        return "Active"


class Fine(models.Model):
    """A fine assessed against a loan returned late.

    Only ever created by books/services.py::return_book, and only when the
    deployment has fines enabled (LibrarySettings.enable_fines) - see
    organization/features.py. One fine per loan: a loan is only ever
    returned once, so there is nothing to accumulate.
    """

    loan = models.OneToOneField(Loan, on_delete=models.PROTECT, related_name="fine")
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    days_overdue = models.PositiveIntegerField()
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"${self.amount} fine for {self.loan}"
