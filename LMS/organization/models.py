from django.db import models


class LibrarySettings(models.Model):
    """Per-deployment configuration: one row per installation (a singleton).

    This is what makes "one codebase, many customer deployments" real -
    every value here is something a specific customer would plausibly want
    different from another, and every field is actually read somewhere in
    the app (see books/services.py, students/context_processors.py, the
    dynamic branding stylesheet in organization/views.py). Fields aren't
    added speculatively for features that don't exist yet.
    """

    # --- Identity -----------------------------------------------------
    organization_name = models.CharField(max_length=150, default="LMS Library")
    library_name = models.CharField(max_length=150, default="LMS Library")
    logo = models.ImageField(upload_to="branding/", null=True, blank=True)
    favicon = models.ImageField(upload_to="branding/", null=True, blank=True)
    support_email = models.EmailField(blank=True)
    support_phone = models.CharField(max_length=40, blank=True)
    address = models.CharField(max_length=255, blank=True)
    opening_hours = models.CharField(max_length=150, blank=True)
    instagram_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    timezone = models.CharField(
        max_length=64,
        default="UTC",
        help_text="An IANA timezone name, e.g. 'Africa/Cairo' or 'America/New_York'.",
    )

    # --- Branding (consumed by organization/views.py's dynamic tokens.css) ---
    primary_color = models.CharField(max_length=7, default="#3C4B9E", help_text="Hex color, e.g. #3C4B9E")
    secondary_color = models.CharField(max_length=7, default="#0F766E")
    accent_color = models.CharField(max_length=7, default="#7C5CBF")
    THEME_LIGHT = "light"
    THEME_DARK = "dark"
    THEME_SYSTEM = "system"
    THEME_CHOICES = [(THEME_LIGHT, "Light"), (THEME_DARK, "Dark"), (THEME_SYSTEM, "System")]
    default_theme_mode = models.CharField(max_length=10, choices=THEME_CHOICES, default=THEME_SYSTEM)

    # --- Loan policy (enforced in books/services.py) -------------------
    loan_duration_days = models.PositiveSmallIntegerField(
        default=14, help_text="Default number of days for a new loan."
    )
    max_books_per_member = models.PositiveSmallIntegerField(
        default=5, help_text="Maximum number of books a member may have on active loan at once."
    )

    # --- Fines (enforced in books/services.py return_book) -------------
    enable_fines = models.BooleanField(default=False)
    fine_per_day = models.DecimalField(max_digits=6, decimal_places=2, default="0.25")
    maximum_fine = models.DecimalField(max_digits=6, decimal_places=2, default="20.00")

    # --- Access toggles (enforced server-side - see organization/access.py) ---
    enable_public_catalog = models.BooleanField(
        default=True, help_text="If off, browsing the book catalog requires login."
    )
    enable_member_portal = models.BooleanField(
        default=True, help_text="If off, profile/loan pages are replaced with a disabled notice."
    )
    enable_email_notifications = models.BooleanField(
        default=True, help_text="If off, the send_due_reminders command sends nothing."
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Library settings"
        verbose_name_plural = "Library settings"

    def __str__(self):
        return self.organization_name

    def save(self, *args, **kwargs):
        self.pk = 1  # enforce singleton
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise RuntimeError("LibrarySettings is a singleton and cannot be deleted.")

    @classmethod
    def get_solo(cls):
        """Return the single settings row, creating it with defaults if needed.

        Deliberately not cached: this is a one-row table, so a plain query
        is negligible - and caching it correctly across multiple app-server
        worker processes would need a shared cache backend (e.g. Redis)
        that this project doesn't otherwise need, plus explicit invalidation
        on every save. A stale-config bug across workers after an admin
        changes settings is a worse outcome than one extra small query per
        request.
        """
        settings_obj, _ = cls.objects.get_or_create(pk=1)
        return settings_obj
