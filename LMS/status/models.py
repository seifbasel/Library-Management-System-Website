from django.db import models

# Create your models here.
class Status(models.Model):

    name = models.CharField(max_length=255)



    def __str__(self):
        return f"{self.name}"
    
    @classmethod
    def get_all_status(cls):
        return cls.objects.all()

