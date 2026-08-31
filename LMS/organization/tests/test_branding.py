from django.test import TestCase
from django.urls import reverse

from organization.models import LibrarySettings
from organization.views import _darken, _tint


class BrandingCssViewTests(TestCase):
    def test_returns_css_with_the_configured_colors(self):
        settings_obj = LibrarySettings.get_solo()
        settings_obj.primary_color = "#123456"
        settings_obj.secondary_color = "#abcdef"
        settings_obj.accent_color = "#654321"
        settings_obj.save()

        response = self.client.get(reverse("branding_css"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/css")
        body = response.content.decode()
        self.assertIn("#123456", body)
        self.assertIn("#abcdef", body)
        self.assertIn("#654321", body)
        self.assertIn("--gradient-brand", body)


class ColorMathTests(TestCase):
    def test_darken_reduces_each_channel(self):
        self.assertEqual(_darken("#ffffff", 0.2), "#cccccc")

    def test_tint_moves_toward_white(self):
        self.assertEqual(_tint("#000000", 0.5), "#808080")

    def test_malformed_color_falls_back_instead_of_crashing(self):
        # Should not raise, even with garbage admin input.
        result = _darken("not-a-color", 0.15)
        self.assertTrue(result.startswith("#"))
        self.assertEqual(len(result), 7)
