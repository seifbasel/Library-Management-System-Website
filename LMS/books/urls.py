from django.urls import path
from books.views import index,show_book

from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', index, name='books.index'),
    path('show', show_book, name='books.show'),
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)