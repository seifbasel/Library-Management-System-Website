from django.urls import path
from students.views import index,login,signup

urlpatterns = [
    path('', index, name='student.index'),
    path('login/', login, name='student.login'),
    path('signup/', signup, name='student.signup'),
]