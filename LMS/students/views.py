from django.shortcuts import render,redirect
from .models import Student
# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse

from students.forms import LoginForm ,SignupForm
from django.contrib.auth import authenticate, login


def index(request):
    return render(request, "students/index.html")

# def profile(request):
#     return render(request, "students/profile.html")


# look here for profile 
def profile(request, id):
    student = Student.get_student(id=id)
    return render( request, "students/profile.html", context={'student': student})

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('students/login.html')
    else:
        form = SignupForm()
    return render(request, 'students/signup.html', {'form': form})

from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponse("Login done")
            else:
                messages.error(request, "Invalid login credentials.")
    else:
        form = LoginForm()
    return render(request, 'students/login.html', {'form': form})



'''
############ old code ################
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

'''


#####################################################


# from .forms import SignupForm, LoginForm
# 
# from django.contrib.auth import authenticate, login
# def signup_view(request):
#     if request.method == 'POST':
#         form = SignupForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('login')
#     else:
#         form = SignupForm()
#     return render(request, 'signup.html', {'form': form})

# def login_view(request):
#     if request.method == 'POST':
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password']
#             user = authenticate(request, username=username, password=password)
#             if user is not None:
#                 login(request, user)
#                 return redirect('dashboard')  # Redirect to the student's dashboard or any other page
#             else:
#                 # Handle invalid login credentials
#                 pass
#     else:
#         form = LoginForm()
#     return render(request, 'login.html', {'form': form})

