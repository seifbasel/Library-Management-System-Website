from django.shortcuts import get_object_or_404, render,redirect
from django.http import HttpResponse
from books.models import Book
from books.forms import BorrowModelForm
from status.models import Status
from students.models import Student

# Create your views here.
def index(request):
    # to show only the book with availlable
    Availlable = Status.objects.get(name='Availlable') 
    books = Book.objects.filter(status=Availlable)
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
            return redirect("books.borrowed")

    return render(request , "books/borrowed.html", context={"form":form})
    
def show_borrowed(request):
    books = Book.objects.filter(user=request.user)
    return render(request , "books/borrowedbooks.html", context={"books":books})

# def view_to_redirect_to(request):
#     #This could be the view that handles the display of created objects"
#     return render(request, "students/index.html")    

def return_to_shelf(request, id):
    book = Book.get_book(id=id)
    Availlable = Status.objects.get(name='Availlable') 
    book.status = Availlable
    book.borrow_date = None
    book.borrow_period = None
    book.user = None
    book.save()
    return redirect("books.borrowed")
    # return HttpResponse("Returned To Self")





