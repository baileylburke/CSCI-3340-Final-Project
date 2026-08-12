from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class RegisterForm(UserCreationForm):
    """Sign-up form for the custom user model.

    UserCreationForm supplies the password1/password2 pair and runs
    AUTH_PASSWORD_VALIDATORS. User.objects.create_user() does neither, so
    building the form is what keeps weak passwords out.
    """

    # display_name is blank=True on the model, but the sign-up page has always
    # asked for it, so it stays required here.
    display_name = forms.CharField(max_length=150)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("display_name", "username", "email")

    def clean_email(self):
        email = self.cleaned_data["email"]
        # The email field is not unique at the database level, so the check
        # lives here. Case-insensitive because addresses are not case
        # sensitive in practice.
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with that email already exists.")
        return email
