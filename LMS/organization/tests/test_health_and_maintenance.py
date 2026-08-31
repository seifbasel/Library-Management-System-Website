from django.test import TestCase, override_settings
from django.urls import reverse


class HealthCheckTests(TestCase):
    def test_returns_ok_with_version_when_database_is_reachable(self):
        response = self.client.get(reverse("health_check"))
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "ok")
        self.assertIn("version", body)

    def test_get_only(self):
        response = self.client.post(reverse("health_check"))
        self.assertEqual(response.status_code, 405)


class MaintenanceModeTests(TestCase):
    @override_settings(MAINTENANCE_MODE=True)
    def test_ordinary_pages_return_503_during_maintenance(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 503)

    @override_settings(MAINTENANCE_MODE=True)
    def test_admin_still_reachable_during_maintenance(self):
        response = self.client.get(reverse("admin:login"))
        self.assertEqual(response.status_code, 200)

    def test_ordinary_pages_work_normally_when_maintenance_mode_is_off(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
