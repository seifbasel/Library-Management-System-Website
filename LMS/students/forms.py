from django import forms
from .models import Student


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
        