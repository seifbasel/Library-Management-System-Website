from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)
from django.contrib.auth.models import User

from students.models import Student
from students.validators import phone_regex


class StyledFormMixin:
    """Applies the shared `.field-input` CSS class to every field's widget.

    Lets built-in Django auth forms (AuthenticationForm, PasswordResetForm,
    etc.) render with `{{ form.field }}` and still pick up the app's design
    system, without needing a template-tags library like widget-tweaks.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} field-input".strip()


class StudentCreationForm(StyledFormMixin, UserCreationForm):
    phone_number = forms.CharField(validators=[phone_regex], max_length=17)
    birthdate = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}), help_text="Enter your birth date")
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ("phone_number", "birthdate", "email")

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered")
        return email


class StudentEditForm(StyledFormMixin, forms.ModelForm):
    phone_number = forms.CharField(validators=[phone_regex], max_length=17, required=False)
    birthdate = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}), required=False)

    class Meta:
        model = Student
        fields = ("name", "phone_number", "email", "birthdate")


class StyledAuthenticationForm(StyledFormMixin, AuthenticationForm):
    pass


class StyledPasswordChangeForm(StyledFormMixin, PasswordChangeForm):
    pass


class StyledPasswordResetForm(StyledFormMixin, PasswordResetForm):
    pass


class StyledSetPasswordForm(StyledFormMixin, SetPasswordForm):
    pass
