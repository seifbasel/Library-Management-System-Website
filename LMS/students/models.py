from django.db import models

# Create your models here.
class Student(models.Model):
    
    id = models.IntegerField(primary_key="true")
    name = models.CharField(max_length=30)
    phone_number = models.IntegerField(max_length=11)
    email = models.EmailField()
    birthdate = models.DateField(max_length=8)
