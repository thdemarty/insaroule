from unittest.mock import patch

from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.translation import override

from accounts.forms import (
    EmailChangeForm,
    PasswordChangeForm,
    PasswordResetForm,
    RegisterForm,
    SetPasswordForm,
)
from accounts.tests.factories import UserFactory


class RegisterTest(TestCase):
    @override_settings(WHITELIST_DOMAINS=["example.com"])
    def test_register_form_valid_and_cleaned_email(self):
        """Test that RegisterForm is valid and cleans email correctly."""
        form_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["email"], "testuser@example.com")

    @override_settings(WHITELIST_DOMAINS=["example.com"])
    def test_register_email_already_exists(self):
        """Test that RegisterForm raises ValidationError if email already exists."""
        existing_user = UserFactory(email="existinguser@example.com")
        existing_user.save()

        form_data = {
            "username": "newuser",
            "email": "existinguser@example.com",
            "password1": "newpassword",
            "password2": "newpassword",
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    @override_settings(WHITELIST_DOMAINS=["example.com"])
    def test_register_disable_registration(self):
        """Test that registration is disabled when ALLOW_REGISTRATION is False."""
        settings.ALLOW_REGISTRATION = False
        with override("en"):
            response = self.client.get(reverse("accounts:register"))
            self.assertIn(
                "Registrations are currently disabled.",
                response.content.decode(),
            )

        settings.ALLOW_REGISTRATION = True
        with override("en"):
            response = self.client.get(reverse("accounts:register"))
            self.assertNotIn(
                "Registrations are currently disabled.",
                response.content.decode(),
            )

    def test_register_whitelisted_domain(self):
        """Test that registration is allowed for whitelisted domains."""
        settings.ALLOW_REGISTRATION = True
        settings.WHITELIST_DOMAINS = ["aaaaaaaaa.xyz"]
        valid_form_data = {
            "username": "testuser",
            "email": "test@aaaaaaaaa.xyz",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        with override("en"):
            form = RegisterForm(data=valid_form_data)
            self.assertTrue(form.is_valid())

        invalid_form_data = {
            "username": "testuser",
            "email": "test@somethingreallydifferenthaha.xyz",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        with override("en"):
            form = RegisterForm(data=invalid_form_data)
            self.assertFalse(form.is_valid())
            self.assertIn("email", form.errors)


class PasswordResetFormTest(TestCase):
    def test_init_each_fields_has_form_control(self):
        """Test that each field in PasswordResetForm has 'form-control' class."""
        form = PasswordResetForm()
        for field in form.fields:
            self.assertIn(
                "form-control", form.fields[field].widget.attrs.get("class", "")
            )

    @override_settings(WHITELIST_DOMAINS=["example.com"])
    @patch("accounts.forms.send_password_reset_email.delay")
    def test_send_mail_called(self, mock_send):
        """Test that send_mail calls the send_password_reset_email task."""
        existing_user = UserFactory(email="testuser@example.com")
        existing_user.save()
        form = PasswordResetForm(data={"email": "testuser@example.com"})
        form.is_valid()
        form.save(domain_override="example.com")
        self.assertTrue(mock_send.called)


class PasswordChangeFormTest(TestCase):
    def test_init_each_fields_has_form_control(self):
        """Test that each field in PasswordChangeForm has 'form-control' class."""
        user = UserFactory()
        form = PasswordChangeForm(user=user)
        for field in form.fields:
            self.assertIn(
                "form-control", form.fields[field].widget.attrs.get("class", "")
            )


class SetPasswordFormTest(TestCase):
    def test_init_each_fields_has_form_control(self):
        """Test that each field in SetPasswordForm has 'form-control' class."""
        user = UserFactory()
        form = SetPasswordForm(user=user)
        for field in form.fields:
            self.assertIn(
                "form-control", form.fields[field].widget.attrs.get("class", "")
            )


class EmailChangeFormTest(TestCase):
    @override_settings(WHITELIST_DOMAINS=["example.com"])
    def test_cleaned_email(self):
        """Test that EmailChangeForm cleans email correctly."""
        existing_user = UserFactory(email="existinguser@example.com")
        existing_user.save()
        form = EmailChangeForm(data={"email": "existinguser@example.com"})
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

        form = EmailChangeForm(data={"email": "newuser@example.com"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["email"], "newuser@example.com")
