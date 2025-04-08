from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

from accounts.models import User


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data["email"]
        email_check = User.objects.filter(email=email)
        domain = email.split("@")[-1]

        # Check if the domain is in the allowed list
        if (
            settings.ALLOW_REGISTRATION
            and domain not in settings.WHITELIST_EMAIL_DOMAINS
        ):
            raise forms.ValidationError(
                _("This email domain is not allowed for registration.")
            )

        # Check if the email already exists
        if email_check.exists():
            raise forms.ValidationError(
                _("This email is already in use. Please use another email.")
            )

        return email
