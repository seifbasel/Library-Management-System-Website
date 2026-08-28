from django.contrib.auth.models import User
from django.test import TestCase

from students.forms import StudentCreationForm, StudentEditForm
from students.models import Student


def _signup_data(**overrides):
    data = {
        "username": "newuser",
        "password1": "CorrectHorseBattery9!",
        "password2": "CorrectHorseBattery9!",
        "phone_number": "+15551234567",
        "birthdate": "1995-05-05",
        "email": "newuser@example.com",
    }
    data.update(overrides)
    return data


class StudentCreationFormTests(TestCase):
    def test_valid_data_is_accepted(self):
        form = StudentCreationForm(data=_signup_data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_rejects_phone_number_with_letters(self):
        form = StudentCreationForm(data=_signup_data(phone_number="not-a-phone"))
        self.assertFalse(form.is_valid())
        self.assertIn("phone_number", form.errors)

    def test_rejects_phone_number_too_short(self):
        form = StudentCreationForm(data=_signup_data(phone_number="12345"))
        self.assertFalse(form.is_valid())
        self.assertIn("phone_number", form.errors)

    def test_accepts_phone_number_with_leading_plus(self):
        form = StudentCreationForm(data=_signup_data(phone_number="+201234567890"))
        self.assertTrue(form.is_valid(), form.errors)

    def test_rejects_duplicate_email(self):
        User.objects.create_user("existing", email="taken@example.com", password="pass12345")
        form = StudentCreationForm(data=_signup_data(email="taken@example.com"))
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)


class StudentEditFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("editor", password="pass12345")
        self.student = Student.objects.create(user=self.user, name="Editor", email="editor@example.com")

    def test_valid_edit_is_accepted(self):
        form = StudentEditForm(
            data={
                "name": "Renamed",
                "phone_number": "+15551234567",
                "email": "renamed@example.com",
                "birthdate": "1990-01-01",
            },
            instance=self.student,
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_rejects_invalid_phone_number(self):
        form = StudentEditForm(
            data={"name": "Renamed", "phone_number": "abc", "email": "renamed@example.com", "birthdate": "1990-01-01"},
            instance=self.student,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("phone_number", form.errors)
