from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse

from organization.models import LibrarySettings


@admin.register(LibrarySettings)
class LibrarySettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Organization", {"fields": ("organization_name", "library_name", "logo", "favicon")}),
        (
            "Contact",
            {"fields": ("support_email", "support_phone", "address", "opening_hours", "timezone")},
        ),
        ("Social", {"fields": ("instagram_url", "twitter_url", "facebook_url")}),
        ("Branding", {"fields": ("primary_color", "secondary_color", "accent_color", "default_theme_mode")}),
        ("Loan policy", {"fields": ("loan_duration_days", "max_books_per_member")}),
        ("Fines", {"fields": ("enable_fines", "fine_per_day", "maximum_fine")}),
        (
            "Feature toggles",
            {"fields": ("enable_public_catalog", "enable_member_portal", "enable_email_notifications")},
        ),
    )

    def has_add_permission(self, request):
        # Singleton: never allow creating a second row.
        return not LibrarySettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        # Skip the list view entirely and go straight to the one row -
        # there is never a meaningful list of "library settings" to browse.
        settings_obj = LibrarySettings.get_solo()
        return redirect(reverse("admin:organization_librarysettings_change", args=[settings_obj.pk]))
