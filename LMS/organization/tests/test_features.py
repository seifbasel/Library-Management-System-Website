from django.test import TestCase

from organization import features
from organization.models import LibrarySettings


class FeatureFlagTests(TestCase):
    def test_is_enabled_reflects_the_current_setting(self):
        settings_obj = LibrarySettings.get_solo()
        settings_obj.enable_fines = False
        settings_obj.save()
        self.assertFalse(features.is_enabled("enable_fines"))

        settings_obj.enable_fines = True
        settings_obj.save()
        self.assertTrue(features.is_enabled("enable_fines"))

    def test_unknown_flag_name_raises_rather_than_silently_returning_false(self):
        with self.assertRaises(ValueError):
            features.is_enabled("enable_something_that_does_not_exist")
