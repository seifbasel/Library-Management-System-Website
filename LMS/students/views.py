from django.shortcuts import render,redirect
from students.forms import StudentCreationForm
from students.models import Student 
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import CreateView
from django.contrib.auth.models import User

def index(request):
    return render(request, "students/index.html")


def profile(request):
    students = Student.get_all_students()
    return render( request, "students/profile.html", context={'students': students} )

## Create
class StudentSignUp(CreateView):
    model = User
    form_class = StudentCreationForm
    success_url = "/students/login"
    template_name = "students/signup.html"

    def form_valid(self, form):
        # Save the User object first
        user = form.save()

        # Map form data to Student model
        student = Student()
        student.name = form.cleaned_data.get('username')
        student.password = user.password
        student.phone_number = form.cleaned_data.get('phone_number')
        student.email = form.cleaned_data.get('email')
        student.birthdate = form.cleaned_data.get('birthdate')
        student.user = user

        # Save the Student object
        student.save()

        return super().form_valid(form)
    

def edit(request, id ):
    student = Student.get_student(id = id)
    if request.method == "POST":
        name = request.POST['name']
        phone_number = request.POST['phone_number']
        email = request.POST['email']
        birthdate = request.POST['birthdate']

        student.name = name
        student.phone_number = phone_number
        student.email = email
        student.birthdate = birthdate

        student.save()
        user = request.user
        user.username = name
        user.save()
        return redirect("student.profile")
        
    return render(request, "students/edit.html")

