from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from students.forms import StyledPasswordChangeForm, StyledPasswordResetForm, StyledSetPasswordForm
from students.views import index

# Django's built-in password change/reset views are wired here, at the root,
# deliberately *not* nested under an app_name namespace - those views call
# reverse() on bare names like 'password_reset_done' internally, and nesting
# them under one broke that (see git history). Each gets our own styled
# form class and a template matching the rest of the app's design system.
urlpatterns = [
    path("", index, name="home"),
    path("admin/", admin.site.urls),
    path("students/", include("students.urls")),
    path("books/", include("books.urls")),
    path("genre/", include("genre.urls")),
    path(
        "accounts/password_change/",
        auth_views.PasswordChangeView.as_view(
            template_name="students/password_change_form.html",
            form_class=StyledPasswordChangeForm,
        ),
        name="password_change",
    ),
    path(
        "accounts/password_change/done/",
        auth_views.PasswordChangeDoneView.as_view(template_name="students/password_change_done.html"),
        name="password_change_done",
    ),
    path(
        "accounts/password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="students/password_reset_form.html",
            form_class=StyledPasswordResetForm,
        ),
        name="password_reset",
    ),
    path(
        "accounts/password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(template_name="students/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "accounts/reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="students/password_reset_confirm.html",
            form_class=StyledSetPasswordForm,
        ),
        name="password_reset_confirm",
    ),
    path(
        "accounts/reset/done/",
        auth_views.PasswordResetCompleteView.as_view(template_name="students/password_reset_complete.html"),
        name="password_reset_complete",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
