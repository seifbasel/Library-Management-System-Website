"""Integration tests for the feature-flag access gates, exercised through
the real views they're applied to (books:index, books:borrowed,
students:profile) - proving the flags are enforced server-side, not just
hidden in a template.
"""

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from organization.models import LibrarySettings


class CatalogAccessTests(TestCase):
    def test_anonymous_user_can_browse_when_public_catalog_enabled(self):
        response = self.client.get(reverse("books:index"))
        self.assertEqual(response.status_code, 200)

    def test_anonymous_user_is_redirected_to_login_when_public_catalog_disabled(self):
        settings_obj = LibrarySettings.get_solo()
        settings_obj.enable_public_catalog = False
        settings_obj.save()

        response = self.client.get(reverse("books:index"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("students:login"), response.url)

    def test_logged_in_user_can_still_browse_when_public_catalog_disabled(self):
        User.objects.create_user("reader", password="pass12345")
        settings_obj = LibrarySettings.get_solo()
        settings_obj.enable_public_catalog = False
        settings_obj.save()

        self.client.login(username="reader", password="pass12345")
        response = self.client.get(reverse("books:index"))
        self.assertEqual(response.status_code, 200)


class MemberPortalAccessTests(TestCase):
    def setUp(self):
        User.objects.create_user("reader", password="pass12345")
        self.client.login(username="reader", password="pass12345")

    def test_profile_accessible_when_member_portal_enabled(self):
        response = self.client.get(reverse("students:profile"))
        self.assertEqual(response.status_code, 200)

    def test_profile_and_loans_return_403_when_member_portal_disabled(self):
        settings_obj = LibrarySettings.get_solo()
        settings_obj.enable_member_portal = False
        settings_obj.save()

        self.assertEqual(self.client.get(reverse("students:profile")).status_code, 403)
        self.assertEqual(self.client.get(reverse("books:borrowed")).status_code, 403)

    def test_anonymous_user_is_redirected_to_login_regardless_of_the_flag(self):
        self.client.logout()
        settings_obj = LibrarySettings.get_solo()
        settings_obj.enable_member_portal = False
        settings_obj.save()

        response = self.client.get(reverse("students:profile"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("students:login"), response.url)
