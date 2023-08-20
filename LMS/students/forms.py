from django import forms
from students.models import Student
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class LoginForm(forms.Form):
    username = forms.CharField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput)



'''
old code 
class Student_form(forms.ModelForm):
    class Meta:
        model=Student
        fields=[
            'name',
            'password',
            'phone_number',
            'email',
            'birthdate',
            
        ]

'''
