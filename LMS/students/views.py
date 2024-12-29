from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from students.forms import StudentCreationForm
from students.models import Student
from django.contrib import messages
from django.urls import reverse

def index(request):
    return render(request, "students/index.html")

@login_required
def profile(request):
    try:
        # Get student profile for the current user, create if doesn't exist
        student, created = Student.objects.get_or_create(
            user=request.user,
            defaults={
                'name': request.user.username,
                'email': request.user.email
            }
        )
        return render(request, "students/profile.html", context={'student': student})
    except Exception as e:
        messages.error(request, f"Error accessing profile: {str(e)}")
        return redirect('student.index')

class StudentSignUp(CreateView):
    model = User
    form_class = StudentCreationForm
    template_name = "students/signup.html"

    def get_success_url(self):
        return reverse('student.login')

    def form_valid(self, form):
        try:
            user = form.save()

            # Create the associated student profile
            student = Student.objects.create(
                user=user,
                name=form.cleaned_data['username'],
                phone_number=form.cleaned_data['phone_number'],
                email=form.cleaned_data['email'],
                birthdate=form.cleaned_data['birthdate']
            )
            messages.success(self.request, "Account created successfully!")
            return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f"Error creating account: {str(e)}")
            return self.form_invalid(form)

@login_required
def edit(request, id):
    student = get_object_or_404(Student, id=id, user=request.user)

    if request.method == "POST":
        try:
            student.name = request.POST['name']
            student.phone_number = request.POST['phone_number']
            student.email = request.POST['email']
            student.birthdate = request.POST['birthdate']
            student.save()

            # Update the associated user
            user = request.user
            user.username = student.name
            user.email = student.email
            user.save()

            messages.success(request, "Profile updated successfully!")
            return redirect("student.profile")
        except Exception as e:
            messages.error(request, f"Error updating profile: {str(e)}")

    return render(request, "students/edit.html", context={'student': student})