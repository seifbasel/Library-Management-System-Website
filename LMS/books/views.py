from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from books.models import Book
from status.models import Status
from django.contrib import messages

def index(request):
    try:
        available_status, created = Status.objects.get_or_create(
            name='Available',
            defaults={'name': 'Available'}
        )
        books = Book.objects.filter(status=available_status)
        return render(request, "books/index.html", context={'books': books})
    except Exception as e:
        messages.error(request, "An error occurred while fetching books.")
        return render(request, "books/index.html", context={'books': []})

def show(request, id):
    book = get_object_or_404(Book, id=id)
    return render(request, "books/show.html", context={'book': book})

def borrow(request, id):
    book = get_object_or_404(Book, id=id)
    if request.method == "POST":
        try:
            status, created = Status.objects.get_or_create(
                name='Borrowed',
                defaults={'name': 'Borrowed'}
            )
            book.status = status
            book.user = request.user
            borrow_period = int(request.POST['borrow_period'])
            borrow_date = date.today()
            return_date = borrow_date + timedelta(days=borrow_period)

            book.borrow_period = borrow_period
            book.borrow_date = borrow_date
            book.return_date = return_date
            book.save()
            messages.success(request, f"Successfully borrowed {book.title}")
            return redirect("books.borrowed")
        except Exception as e:
            messages.error(request, "An error occurred while borrowing the book.")
            return render(request, "books/borrow.html")
    return render(request, "books/borrow.html")

def show_borrowed(request):
    books = Book.objects.filter(user=request.user)
    return render(request, "books/borrowedbooks.html", context={"books": books})

def return_to_shelf(request, id):
    try:
        book = get_object_or_404(Book, id=id)
        available_status, created = Status.objects.get_or_create(
            name='Available',
            defaults={'name': 'Available'}
        )
        book.status = available_status
        book.borrow_date = None
        book.borrow_period = None
        book.return_date = None
        book.user = None
        book.save()
        messages.success(request, f"Successfully returned {book.title}")
        return redirect("books.borrowed")
    except Exception as e:
        messages.error(request, "An error occurred while returning the book.")
        return redirect("books.borrowed")