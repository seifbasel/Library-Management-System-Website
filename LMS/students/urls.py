from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from students.forms import StyledAuthenticationForm
from students.views import StudentSignUp, edit, profile

app_name = "students"

urlpatterns = [
    path(
        "login/",
        LoginView.as_view(template_name="students/login.html", authentication_form=StyledAuthenticationForm),
        name="login",
    ),
    path(
        "logout/",
        LogoutView.as_view(template_name="students/logout.html", next_page="students:login"),
        name="logout",
    ),
    path("profile/", profile, name="profile"),
    path("signup/", StudentSignUp.as_view(), name="signup"),
    path("<int:id>/edit/", edit, name="edit"),
]
