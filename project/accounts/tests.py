from unittest.mock import patch

from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.translation import override

from accounts.forms import RegisterForm
from accounts.models import User
from accounts.tasks import send_verification_email


class RegisterTest(TestCase):
    def test_register_email_already_exists(self):
        existing_user = User.objects.create(
            username="existinguser",
            email="existinguser@example.com",
            password="password123",
        )
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

    def test_register_disable_registration(self):
        settings.ALLOW_REGISTRATION = False
        with override("en"):
            response = self.client.get(reverse("accounts:register"))
            self.assertIn(
                "Registrations are currently disabled.", response.content.decode()
            )

        settings.ALLOW_REGISTRATION = True
        with override("en"):
            response = self.client.get(reverse("accounts:register"))
            self.assertNotIn(
                "Registrations are currently disabled.", response.content.decode()
            )


@override_settings(CELERY_TASK_ALWAYS_EAGER=True, CELERY_TASK_EAGER_PROPAGATES=True)
class VerifyEmailTest(TestCase):
    # Test that the verification email task has been called
    @patch("accounts.tasks.send_verification_email.delay")
    def test_send_verification_email(self, mock_send):
        user = User.objects.create_user(
            username="testuser",
            email="test@example.org",
            password="test",
        )
        token = "dummy-token"
        site_base_url = "http://testserver"

        send_verification_email.delay(
            user.username, user.pk, user.email, token, site_base_url
        )

        self.assertTrue(mock_send.called)
