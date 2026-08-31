from io import StringIO
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.management import CommandError, call_command
from django.test import TestCase

from organization.models import LibrarySettings


class SetupOrganizationCommandTests(TestCase):
    def test_configures_organization_settings(self):
        call_command(
            "setup_organization",
            "--organization-name=Riverside School",
            "--primary-color=#1F6F4A",
            "--timezone=America/Chicago",
            stdout=StringIO(),
        )

        settings_obj = LibrarySettings.get_solo()
        self.assertEqual(settings_obj.organization_name, "Riverside School")
        self.assertEqual(settings_obj.library_name, "Riverside School")  # defaults to org name
        self.assertEqual(settings_obj.primary_color, "#1F6F4A")
        self.assertEqual(settings_obj.timezone, "America/Chicago")

    def test_creates_admin_user_when_requested(self):
        call_command(
            "setup_organization",
            "--organization-name=Test Org",
            "--admin-username=neworgadmin",
            "--admin-password=SuperSecret123!",
            "--admin-email=admin@test.example",
            stdout=StringIO(),
        )

        user = User.objects.get(username="neworgadmin")
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_does_not_duplicate_or_error_if_admin_already_exists(self):
        User.objects.create_user("existingadmin", password="whatever")
        # Should not raise, and should not touch the existing user.
        call_command(
            "setup_organization",
            "--organization-name=Test Org",
            "--admin-username=existingadmin",
            "--admin-password=SomethingElse123!",
            stdout=StringIO(),
        )
        self.assertEqual(User.objects.filter(username="existingadmin").count(), 1)

    def test_raises_if_admin_username_given_with_no_password_available(self):
        # No --admin-password given, and the interactive prompt (mocked
        # here so the test doesn't block on real stdin) also comes back
        # empty - the command must refuse rather than create a passwordless
        # superuser.
        with patch("getpass.getpass", return_value=""):
            with self.assertRaises(CommandError):
                call_command(
                    "setup_organization",
                    "--organization-name=Test Org",
                    "--admin-username=someone",
                    stdout=StringIO(),
                )
        self.assertFalse(User.objects.filter(username="someone").exists())
