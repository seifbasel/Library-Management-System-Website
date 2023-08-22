from django.db import models
from genre.models import Genre
from status.models import Status
from django.urls import reverse
from django.contrib.auth.models import User
# Create your models here.
#hello
class Book(models.Model):

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    image = models.ImageField(upload_to='books/images',null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    pages = models.IntegerField(null=True, blank=True)
    active = models.BooleanField(default=True, null=True, blank=True)
    status = models.ForeignKey(Status, on_delete= models.CASCADE, null= True, related_name="books", default="Availlable")
    borrow_date = models.DateField(null=True, blank=True)
    borrow_period = models.IntegerField(null=True, blank=True)
    genre =models.ForeignKey(Genre, on_delete= models.CASCADE, null= True, related_name="books")
    user =models.ForeignKey(User, on_delete= models.CASCADE, null= True, blank=True, related_name="books")


    def __str__(self):
        return f"{self.title}"
    
    @classmethod
    def get_all_books(cls):
        return cls.objects.all()

    @classmethod
    def get_book(cls, id):
        return cls.objects.get(id = id)

    def get_image_url(self):
        return f"/media/{self.image}"
    
    def get_show_url(self):
        return reverse("books.show", args=[self.id])
    
    def get_borrow_url(self):
        return reverse("books.borrow", args=[self.id])
    
    def get_return_to_shelf_url(self):
        return reverse("books.shelf", args=[self.id])
    # def get_show_url(self):
    #     return reverse("books.borrow", args=[self.id])
