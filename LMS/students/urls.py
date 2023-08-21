from django.urls import path, include
from students.views import index, profile, StudentSignUp# ,login
from django.contrib.auth import login, logout


    

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('index/', index, name='student.index'),
    path('login/', login, name='student.login'),
    path('profile/', profile, name='student.profile'),
<<<<<<< HEAD
=======
    path('signup/', StudentSignUp.as_view(),name='student.signup'),
    
>>>>>>> e0e491146f8cd6d70c30aa99494cb73e906be496
    # path('signup/', student_creat_view,name='student.signup'),
]