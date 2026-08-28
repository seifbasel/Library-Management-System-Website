from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from books.exceptions import BookNotAvailableError, LoanAlreadyReturnedError
from books.forms import BorrowForm
from books.models import Book
from books.services import borrow_book, return_book
from genre.models import Genre
from loans.models import Loan

BOOKS_PER_PAGE = 12


def index(request):
    query = request.GET.get("q", "").strip()
    genre_id = request.GET.get("genre", "")
    availability = request.GET.get("availability", "")

    books = Book.objects.select_related("genre", "status")

    if query:
        books = books.filter(Q(title__icontains=query) | Q(author__icontains=query))
    if genre_id:
        books = books.filter(genre_id=genre_id)
    if availability == "available":
        # Deliberately not `.exclude(loans__returned_at__isnull=True)`: Django
        # translates that via a LEFT JOIN, and a book with *no* loans at all
        # also has a NULL joined returned_at, so it would be wrongly excluded
        # too. Excluding by an explicit id__in subquery avoids that trap.
        currently_borrowed = Loan.objects.filter(returned_at__isnull=True).values("book_id")
        books = books.exclude(id__in=currently_borrowed)

    paginator = Paginator(books, BOOKS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "books": page_obj.object_list,
        "genres": Genre.objects.all(),
        "query": query,
        "selected_genre": genre_id,
        "selected_availability": availability,
    }
    return render(request, "books/index.html", context=context)


def show(request, id):
    book = get_object_or_404(Book.objects.select_related("genre", "status"), id=id)
    return render(request, "books/show.html", context={"book": book})


@login_required
def borrow(request, id):
    book = get_object_or_404(Book, id=id)
    if request.method == "POST":
        form = BorrowForm(request.POST)
        if form.is_valid():
            try:
                borrow_book(book=book, borrower=request.user, period_days=form.cleaned_data["borrow_period"])
            except BookNotAvailableError as exc:
                messages.error(request, str(exc))
            else:
                messages.success(request, f"Successfully borrowed {book.title}")
                return redirect("books:borrowed")
        return render(request, "books/borrow.html", context={"book": book, "form": form})
    return render(request, "books/borrow.html", context={"book": book, "form": BorrowForm()})


@login_required
def show_borrowed(request):
    loans = Loan.objects.filter(borrower=request.user, returned_at__isnull=True).select_related(
        "book", "book__genre", "book__status"
    )
    return render(request, "books/borrowedbooks.html", context={"loans": loans})


@login_required
@require_POST
def return_to_shelf(request, id):
    loan = get_object_or_404(Loan, book_id=id, borrower=request.user, returned_at__isnull=True)
    try:
        return_book(loan=loan)
    except LoanAlreadyReturnedError as exc:
        messages.error(request, str(exc))
    else:
        messages.success(request, f"Successfully returned {loan.book.title}")
    return redirect("books:borrowed")
