from django.urls import path
from students.views import student

urlpatterns = [
    path('',student, name='student'),
]