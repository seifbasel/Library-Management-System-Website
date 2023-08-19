from django.db import models



class Genre(models.Model):

    name = models.CharField(max_length=255)


    def __str__(self):
        return f"{self.title}"
    
    @classmethod
    def get_all_genres(cls):
        return cls.objects.all()

