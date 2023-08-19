from django.db import models

# Create your models here.
class Book(models.Model):
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('rented', 'Rented'),
        ('sold', 'Sold'),
    )

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    image = models.ImageField(upload_to='books/images',null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    active = models.BooleanField(default=True, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')
    rent_date = models.DateField(null=True, blank=True)
    rent_period = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.title}"
    
    @classmethod
    def get_all_books(cls):
        return cls.objects.all()

    # def get_image_url(self):
    #     return f"/media/{self.image}"