from django.urls import path, include
from students.views import index, profile, StudentSignUp# ,login
from django.contrib.auth import login, logout


    

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('index/', index, name='student.index'),
    path('login/', login, name='student.login'),
    path('profile/', profile, name='student.profile'),
    path('signup/', StudentSignUp.as_view(),name='student.signup'),
    
    # path('signup/', student_creat_view,name='student.signup'),
]