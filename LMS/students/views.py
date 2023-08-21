from django.shortcuts import render,redirect
from students.forms import Student_form
from students.models import Student
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import CreateView
def index(request):
    return render(request, "students/index.html")



def profile(request):

    return render(request, "students/profile.html")




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
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
class StudentSignUp(CreateView):
    model = User
    form_class = UserCreationForm
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

        # Save the Student object
        student.save()

        return super().form_valid(form)