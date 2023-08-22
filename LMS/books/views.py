from django.shortcuts import get_object_or_404, render,redirect
from django.http import HttpResponse
from books.models import Book
from status.models import Status

# Create your views here.
def index(request):
    books = Book.get_all_books()
    return render( request, "books/index.html", context={'books': books} )


def show(request, id):
    book = Book.get_book(id=id)
    return render( request, "books/show.html", context={'book': book})

def borrow(request, id):
    book = Book.get_book(id=id)
    status = Status.objects.get(name='Borrowed')
    book.status = status
    book.save()
    return HttpResponse("<h1>Borrowed</h1>")
    
