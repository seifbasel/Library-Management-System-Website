from django.urls import path

from books.views import borrow, index, return_to_shelf, show, show_borrowed

app_name = "books"

urlpatterns = [
    path("", index, name="index"),
    path("borrowed/", show_borrowed, name="borrowed"),
    path("<int:id>/", show, name="show"),
    path("<int:id>/borrow/", borrow, name="borrow"),
    path("<int:id>/return/", return_to_shelf, name="return"),
]
