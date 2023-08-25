from django.shortcuts import render,redirect
from django.http import HttpResponse
from books.models import Book
from status.models import Status


# Create your views here.
def index(request):
    # to show only the book with availlable status
    Availlable = Status.objects.get(name='Availlable') 
    books = Book.objects.filter(status=Availlable)
    return render( request, "books/index.html", context={'books': books} )


def show(request, id):
    book = Book.get_book(id=id)
    return render( request, "books/show.html", context={'book': book})

## Borrow Function
from datetime import date, timedelta
def borrow(request, id):
    book = Book.get_book(id=id)
    if request.method == "POST":
            status = Status.objects.get(name='Borrowed')
            book.status = status
            book.user = request.user
            borrow_period = int(request.POST['borrow_period'])
            borrow_date = date.today()
            return_date = borrow_date + timedelta(days=borrow_period)

            book.borrow_period = borrow_period
            book.borrow_date = borrow_date
            book.return_date = return_date
            book.save()
            return redirect("books.borrowed")
    return render(request , "books/borrow.html")
            




def show_borrowed(request):
    books = Book.objects.filter(user=request.user)
    return render(request , "books/borrowedbooks.html", context={"books":books})


def return_to_shelf(request, id):
    book = Book.get_book(id=id)
    Availlable = Status.objects.get(name='Availlable') 
    book.status = Availlable
    book.borrow_date = None
    book.borrow_period = None
    book.return_date =None
    book.user = None
    book.save()
    return redirect("books.borrowed")
    # return HttpResponse("Returned To Self")





