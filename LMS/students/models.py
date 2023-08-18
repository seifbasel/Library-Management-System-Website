from django.db import models

# Create your models here.
class Student(models.Model):
    name = models.CharField(max_length=255)
    phone_number = models.IntegerField(max_length=11, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    birthdate = models.DateField(max_length=8, null=True, blank=True)


    def __str__(self):
        return f"{self.name}"
