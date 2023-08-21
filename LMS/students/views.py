from django.shortcuts import render,redirect
from students.forms import Student_form
from students.models import Student
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import CreateView
def index(request):
    return render(request, "students/index.html")

# def profile(request):
#     return render(request, "students/profile.html")


# look here for profile 
def profile(request, id):
    student = Student.get_student(id=id)
    return render( request, "students/profile.html", context={'student': student})

# def login(request):
#     return render(request, "students/login.html")


# def signup(request):
#     return render(request, "students/signup.html")

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

class StudentSignUp(CreateView):
    model = Student
    form_class = Student_form
    success_url = "/students/login"
    template_name = "students/signup.html"