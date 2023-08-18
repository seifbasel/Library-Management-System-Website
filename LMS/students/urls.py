from django.urls import path
from students.views import index,login

urlpatterns = [
    path('', index, name='student.index'),
    path('login/', login, name='student.login'),
]