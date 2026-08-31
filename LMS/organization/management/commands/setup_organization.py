"""One-time onboarding for a new deployment.

Non-interactive by design (arguments, not prompts) so it can run as part of
a repeatable deployment process (Docker entrypoint, CI/CD step, etc.) - see
docs/deployment.md. Safe to re-run: updates the existing LibrarySettings
singleton and skips creating the admin user if that username already exists.

Example:
    python manage.py setup_organization \\
        --organization-name "Riverside School" \\
        --library-name "Riverside Library" \\
        --admin-username admin --admin-email admin@riverside.example \\
        --admin-password "change-me-immediately" \\
        --primary-color "#1F6F4A" --timezone "America/Chicago"
"""

import getpass

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from organization.models import LibrarySettings


class Command(BaseCommand):
    help = "Configure a new deployment's organization identity, branding, and initial admin user."

    def add_arguments(self, parser):
        parser.add_argument("--organization-name", required=True)
        parser.add_argument("--library-name", default=None, help="Defaults to the organization name.")
        parser.add_argument("--timezone", default="UTC")
        parser.add_argument("--primary-color", default="#3C4B9E")
        parser.add_argument("--secondary-color", default="#0F766E")
        parser.add_argument("--accent-color", default="#7C5CBF")
        parser.add_argument("--support-email", default="")
        parser.add_argument("--support-phone", default="")
        parser.add_argument("--admin-username", default=None, help="If omitted, no admin user is created.")
        parser.add_argument("--admin-email", default="")
        parser.add_argument(
            "--admin-password",
            default=None,
            help="If omitted (and --admin-username is given), you'll be prompted securely.",
        )

    def handle(self, *args, **options):
        settings_obj = LibrarySettings.get_solo()
        settings_obj.organization_name = options["organization_name"]
        settings_obj.library_name = options["library_name"] or options["organization_name"]
        settings_obj.timezone = options["timezone"]
        settings_obj.primary_color = options["primary_color"]
        settings_obj.secondary_color = options["secondary_color"]
        settings_obj.accent_color = options["accent_color"]
        settings_obj.support_email = options["support_email"]
        settings_obj.support_phone = options["support_phone"]
        settings_obj.save()
        self.stdout.write(self.style.SUCCESS(f"Configured organization: {settings_obj.organization_name}"))

        admin_username = options["admin_username"]
        if admin_username:
            if User.objects.filter(username=admin_username).exists():
                self.stdout.write(f"Admin user '{admin_username}' already exists - leaving it as-is.")
            else:
                password = options["admin_password"] or getpass.getpass(
                    f"Password for new admin user '{admin_username}': "
                )
                if not password:
                    raise CommandError("An admin password is required to create the admin user.")
                User.objects.create_superuser(
                    username=admin_username,
                    email=options["admin_email"],
                    password=password,
                )
                self.stdout.write(self.style.SUCCESS(f"Created admin user: {admin_username}"))

        self.stdout.write(self.style.SUCCESS("Setup complete. Fine-tune the rest in Django admin > Library settings."))
