from django.test import TestCase

from organization.models import LibrarySettings


class LibrarySettingsSingletonTests(TestCase):
    def test_new_settings_use_the_default_brand_colors(self):
        settings_obj = LibrarySettings()

        self.assertEqual(settings_obj.primary_color, "#3C4B9E")
        self.assertEqual(settings_obj.secondary_color, "#0F766E")
        self.assertEqual(settings_obj.accent_color, "#7C5CBF")

    def test_get_solo_creates_a_row_with_defaults_on_first_call(self):
        self.assertEqual(LibrarySettings.objects.count(), 0)
        settings_obj = LibrarySettings.get_solo()
        self.assertEqual(settings_obj.pk, 1)
        self.assertEqual(LibrarySettings.objects.count(), 1)

    def test_get_solo_returns_the_same_row_on_repeated_calls(self):
        first = LibrarySettings.get_solo()
        first.organization_name = "Riverside Library"
        first.save()

        second = LibrarySettings.get_solo()
        self.assertEqual(second.pk, first.pk)
        self.assertEqual(second.organization_name, "Riverside Library")

    def test_save_always_forces_pk_1_even_on_a_fresh_instance(self):
        settings_obj = LibrarySettings(organization_name="Should still be singleton")
        settings_obj.save()
        self.assertEqual(settings_obj.pk, 1)
        self.assertEqual(LibrarySettings.objects.count(), 1)

    def test_delete_is_refused(self):
        settings_obj = LibrarySettings.get_solo()
        with self.assertRaises(RuntimeError):
            settings_obj.delete()
        self.assertEqual(LibrarySettings.objects.count(), 1)
