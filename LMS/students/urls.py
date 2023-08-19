from django.urls import path
from students.views import index,login,signup,student_creat_view

urlpatterns = [
    path('', index, name='student.index'),
    path('login/', login, name='student.login'),
    # path('signup/', signup, name='student.signup'),
    path('signup/', student_creat_view,name='student.signup'),
    
]