from django.urls import path
from books.views import index, show, borrow, show_borrowed, return_to_shelf
from django.contrib.auth.decorators import login_required
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', index, name='books.index'),
    path("<int:id>", show, name="books.show"),
    path("books/<int:id>", login_required(borrow), name="books.borrow"),
    path("bb", show_borrowed, name="books.borrowed"),
    path("shelf/<int:id>", return_to_shelf, name="books.shelf")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)