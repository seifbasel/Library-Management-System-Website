from django.urls import path
from students.views import index,login, profile, StudentSignUp

urlpatterns = [
    path('', index, name='student.index'),
    path('login/', login, name='student.login'),
    path('profile/', profile, name='student.profile'),
    path('signup/', StudentSignUp.as_view(),name='student.signup'),
    
]