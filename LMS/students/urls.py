from django.urls import path, include
from students.views import index, profile, StudentSignUp, edit
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('', index, name='student.index'),
    path('login/', LoginView.as_view(template_name='students/login.html'), name='student.login'),
    path('logout/', LogoutView.as_view(template_name='students/logout.html', next_page='student.login'), name='student.logout'),
    path('profile/', profile, name='student.profile'),
    path('signup/', StudentSignUp.as_view(), name='student.signup'),
    path('<int:id>/edit/', edit, name='student.edit'),
    path('', include('django.contrib.auth.urls')),
]