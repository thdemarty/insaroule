from django import forms
from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm
from django.contrib.auth.forms import PasswordResetForm as DjangoPasswordResetForm
from django.contrib.auth.forms import SetPasswordForm as DjangoSetPasswordForm
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from accounts.models import User
from accounts.tasks import send_password_reset_email


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _field_name, field in self.fields.items():
            field.widget.attrs.update({"class": "form-control"})

    def clean_email(self):
        email = self.cleaned_data["email"]

        # Check if domain is whitelisted
        domain = email.split("@")[1]
        if settings.WHITELIST_DOMAINS == ["*"]:
            # Allow all domains
            pass
        elif domain not in settings.WHITELIST_DOMAINS:
            allowed_domains = [f"@{domain}" for domain in settings.WHITELIST_DOMAINS]
            message = _(
                "Only emails with whitelisted domains are allowed to register. Allowed domains are:"
            )
            message += f"{', '.join(allowed_domains)}"
            raise forms.ValidationError(message)

        # Check if email is already in use
        email_check = User.objects.filter(email=email)
        if email_check.exists():
            raise forms.ValidationError(
                _("This email is already in use. Please use another email."),
            )

        return email


class PasswordResetForm(DjangoPasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _field_name, field in self.fields.items():
            field.widget.attrs.update({"class": "form-control"})

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        context["user"] = context["user"].pk

        send_password_reset_email.delay(
            subject_template_name=subject_template_name,
            email_template_name="registration/password_reset/email.html",
            context=context,
            from_email=from_email,
            to_email=to_email,
            html_email_template_name=html_email_template_name,
        )


class PasswordChangeForm(DjangoPasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _field_name, field in self.fields.items():
            field.widget.attrs.update({"class": "form-control"})


class SetPasswordForm(DjangoSetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _field_name, field in self.fields.items():
            field.widget.attrs.update({"class": "form-control"})


class EmailChangeForm(forms.Form):
    email = forms.EmailField(
        label=_("New Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data["email"]
        email_check = User.objects.filter(email=email)
        if email_check.exists():
            raise forms.ValidationError(
                _("This email is already in use. Please use another email."),
            )

        return email
