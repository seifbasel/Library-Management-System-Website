from django.urls import path
from students.views import index, profile, StudentSignUp# ,login
from django.contrib.auth import login, logout


urlpatterns = [
    path('', index, name='student.index'),
    path('login/', login, name='student.login'),
    path('profile/', profile, name='student.profile'),
<<<<<<< HEAD
    path('signup/', StudentSignUp.as_view(),name='student.signup'),
    
=======
    path('signup/', student_creat_view,name='student.signup'),
>>>>>>> 80f4503851c093f78a31c3bdf51d4c7f2b2e9014
]