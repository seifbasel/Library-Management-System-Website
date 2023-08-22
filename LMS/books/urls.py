from django.urls import path
from books.views import index,show,borrow

from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', index, name='books.index'),
    path("<int:id>", show, name="books.show"),
    path("books/<int:id>", borrow, name="books.borrow")
    # path("creat", book_creat_view, name="books.creat"),
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)