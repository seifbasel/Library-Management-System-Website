from django.shortcuts import render,redirect
from .forms import Student_form
from .models import Student
# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return render(request, "students/index.html")

# def profile(request):
#     return render(request, "students/profile.html")

def profile(request, id):
    student = Student.get_all_students(id=id)
    return render( request, "students/profile.html", context={'student': student})

def login(request):
    return render(request, "students/login.html")


def signup(request):
    return render(request, "students/signup.html")

def student_creat_view(request):
    # form=Student_form(request.POST or None)
    # if form.is_valid():
    #     form.save()
    # form=Student_form()
    
    # context={
    #     'form':form
    # }
    # return render(request, "students/signup.html",context)
    student = Student.get_all_students()

    if request.method == "POST":
        name = request.POST['name']
        password = request.POST['password']
        phonenumber = request.POST['phonenumber']
        email = request.POST['email']
        birthdate= request.POST['birthdate']
    
        student=Student()
        student.name=name
        student.password = password
        student.phone_number = phonenumber
        student.email = email
        student.birthdate=birthdate
        student.save()
        

        return redirect('student.index')
    return render(request,'students/signup.html',context={'student':student})