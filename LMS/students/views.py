from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView

from books.models import Book
from loans.models import Loan
from organization.access import member_portal_view
from students.forms import StudentCreationForm, StudentEditForm
from students.models import Student


def index(request):
    currently_borrowed = Loan.objects.filter(returned_at__isnull=True).values("book_id")

    most_borrowed = (
        Book.objects.annotate(loan_count=Count("loans")).filter(loan_count__gt=0).order_by("-loan_count")[:8]
    )

    context = {
        "new_releases": Book.objects.exclude(image="").order_by("-created_at")[:8],
        "most_borrowed": most_borrowed,
        "total_books_count": Book.objects.count(),
        "available_books_count": Book.objects.exclude(id__in=currently_borrowed).count(),
    }
    return render(request, "students/index.html", context=context)


@member_portal_view
def profile(request):
    student, _created = Student.objects.get_or_create(
        user=request.user,
        defaults={
            "name": request.user.username,
            "email": request.user.email,
        },
    )

    active_loans = Loan.objects.filter(borrower=request.user, returned_at__isnull=True)
    context = {
        "student": student,
        "active_loans_count": active_loans.count(),
        "overdue_count": active_loans.filter(due_at__lt=timezone.localdate()).count(),
        "total_loans_count": Loan.objects.filter(borrower=request.user).count(),
        "recent_loans": Loan.objects.filter(borrower=request.user).select_related("book")[:5],
    }
    return render(request, "students/profile.html", context=context)


class StudentSignUp(CreateView):
    model = User
    form_class = StudentCreationForm
    template_name = "students/signup.html"

    def get_success_url(self):
        return reverse("students:login")

    def form_valid(self, form):
        with transaction.atomic():
            user = form.save()
            Student.objects.create(
                user=user,
                name=form.cleaned_data["username"],
                phone_number=form.cleaned_data["phone_number"],
                email=form.cleaned_data["email"],
                birthdate=form.cleaned_data["birthdate"],
            )
        self.object = user
        messages.success(self.request, "Account created successfully!")
        return redirect(self.get_success_url())


@member_portal_view
def edit(request, id):
    student = get_object_or_404(Student, id=id, user=request.user)

    if request.method == "POST":
        form = StudentEditForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            # Keep the login email in sync with the profile email; the
            # username is intentionally left untouched - it's the login
            # identifier, not an editable display name.
            request.user.email = form.cleaned_data["email"]
            request.user.save(update_fields=["email"])
            messages.success(request, "Profile updated successfully!")
            return redirect("students:profile")
    else:
        form = StudentEditForm(instance=student)

    return render(request, "students/edit.html", context={"student": student, "form": form})
