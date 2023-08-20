from django.urls import path,include
from students.views import index,login,profile,signup_view, login_view#,signup,student_creat_view

urlpatterns = [
    path('', index, name='student.index'),
    path('login/', login, name='student.login'),
    path('profile/', profile, name='student.profile'),
    path('signup/', signup_view, name='students.signup'),
    path('login/', login_view, name='students.login'),
    

    
]