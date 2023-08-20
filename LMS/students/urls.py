from django.urls import path
from students.views import index,login,signup,student_creat_view,profile

urlpatterns = [
    path('', index, name='student.index'),
    path('login/', login, name='student.login'),
    path('profile/', profile, name='student.profile'),
    # <int:id>  look here 
    path('signup/', student_creat_view,name='student.signup'),
    
]