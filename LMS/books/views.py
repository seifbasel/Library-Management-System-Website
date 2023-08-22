from django.shortcuts import get_object_or_404, render,redirect
from django.http import HttpResponse
from books.models import Book
from books.forms import BorrowModelForm
from status.models import Status
from students.models import Student

# Create your views here.
def index(request):
    books = Book.get_all_books()
    return render( request, "books/index.html", context={'books': books} )


def show(request, id):
    book = Book.get_book(id=id)
    return render( request, "books/show.html", context={'book': book})

def borrow(request, id):
    book = Book.get_book(id=id)
    form = BorrowModelForm(instance=book)
    if request.POST:
        form = BorrowModelForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            status = Status.objects.get(name='Borrowed')
            book.status = status
            book.user = request.user
            book.save()
            form.save()
            # return HttpResponse("<h1>Borrowed</h1>")
            return redirect("books/borrowed.html")

    return render(request , "books/borrowed.html", context={"form":form})
    
def show_borrowed(request):
    books = Book.objects.filter(user=request.user)
    return render(request , "books/borrowedbooks.html", context={"books":books})
    
