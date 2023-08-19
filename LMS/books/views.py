from django.shortcuts import render
from books.models import Book
# Create your views here.
def index(request):
    books = Book.get_all_books()
    return render( request, "books/index.html", context={'books': books} )