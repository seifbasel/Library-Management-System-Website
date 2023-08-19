from django.shortcuts import render
from .forms import Student_form
from .models import Student
# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return render(request, "students/index.html")


def login(request):
    return render(request, "students/login.html")


def signup(request):
    return render(request, "students/signup.html")

def student_creat_view(request):
    # obj=Student.objects.get(ID=1)
    form=Student_form(request.POST or None)
    if form.is_valid():
        form.save()
    form=Student_form()
    
    context={
        'form':form
    }
    
    # context={
    #     'name':obj.name,
    #     'password':obj.password,
    #     'phone_number':obj.phone_number,
    # }
    
    return render(request, "students/signup.html",context)
    