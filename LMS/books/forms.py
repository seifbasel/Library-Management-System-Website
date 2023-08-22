from django import forms
from books.models import Book

class BorrowModelForm(forms.ModelForm):
    borrow_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    borrow_period = forms.IntegerField(label="Enter Days")
    class Meta:
        model = Book
        fields = ['borrow_date', 'borrow_period']
