from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from students.views import index

urlpatterns = [
    path('', index, name='student.index'),
    path('admin/', admin.site.urls),
    path("students/", include('students.urls')),
    path("books/", include('books.urls')),
    path("genre/", include('genre.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)