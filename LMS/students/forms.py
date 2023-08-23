
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class StudentCreationForm(UserCreationForm):
    phone_number = forms.CharField(max_length=20)
    birthdate = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    email = forms.EmailField()

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('phone_number', 'birthdate', 'email')





