from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from students.validators import phone_regex


class Student(models.Model):
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=17, validators=[phone_regex], null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.name}"

    def get_profile_url(self):
        return reverse("students:profile")

    def get_edit_url(self):
        return reverse("students:edit", args=[self.id])
