from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.urls import reverse


class PasswordResetFlowTests(TestCase):
    """Regression tests for the built-in auth URLs living outside any
    app_name namespace - django.contrib.auth's views call reverse() on
    bare names like 'password_reset_done' internally, so nesting the
    include under an app-namespaced urls.py breaks it with NoReverseMatch.
    """

    def setUp(self):
        User.objects.create_user("resetuser", email="resetuser@example.com", password="pass12345")

    def test_password_reset_page_loads(self):
        response = self.client.get(reverse("password_reset"))
        self.assertEqual(response.status_code, 200)

    def test_submitting_password_reset_sends_an_email_and_redirects(self):
        response = self.client.post(reverse("password_reset"), {"email": "resetuser@example.com"})
        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["resetuser@example.com"])

    def test_password_change_page_loads_for_logged_in_user(self):
        self.client.login(username="resetuser", password="pass12345")
        response = self.client.get(reverse("password_change"))
        self.assertEqual(response.status_code, 200)
