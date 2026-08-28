# books/models.py
from django.db import models
from django.templatetags.static import static
from django.urls import reverse

from genre.models import Genre
from status.models import Status


def get_default_status_id():
    """PK of the 'Available' Status row, creating it if it doesn't exist yet.

    Resolved by name rather than a hardcoded PK so it doesn't depend on
    row-insertion order in a fresh database.
    """
    return Status.objects.get_or_create(name="Available")[0].pk


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    image = models.ImageField(upload_to="books/images", null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    pages = models.IntegerField(null=True, blank=True)
    status = models.ForeignKey(
        Status,
        on_delete=models.PROTECT,
        null=True,
        related_name="books",
        default=get_default_status_id,
    )
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, null=True, related_name="books")
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title}"

    @property
    def is_available(self):
        """Whether the book currently has no active (unreturned) loan."""
        return not self.loans.filter(returned_at__isnull=True).exists()

    @property
    def active_loan(self):
        """The book's current active loan, if any."""
        return self.loans.filter(returned_at__isnull=True).select_related("borrower").first()

    def get_image_url(self):
        if self.image:
            return self.image.url
        return static("students/images/book-placeholder.svg")

    def get_show_url(self):
        return reverse("books:show", args=[self.id])

    def get_borrow_url(self):
        return reverse("books:borrow", args=[self.id])

    def get_return_to_shelf_url(self):
        return reverse("books:return", args=[self.id])
