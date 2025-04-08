from django.test import TestCase
from django.conf import settings
from accounts.forms import RegisterForm
from accounts.models import User


class RegisterFormTest(TestCase):
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
            "password1": "btnroipbrtpbpnpo",
            "password2": "btnroipbrtpbpnpo",
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_register_disable_registration(self):
        settings.ALLOW_REGISTRATION = False
        response = self.client.get("/register/")
        self.assertIn("Les inscriptions sont désactivées.", response.content.decode())

        settings.ALLOW_REGISTRATION = True
        response = self.client.get("/register/")
        self.assertNotIn(
            "Les inscriptions sont désactivées.", response.content.decode()
        )

    def test_register_whitelist_domain(self):
        form_data = {
            "username": "newuser",
            "email": "user@authorized.com",
            "password1": "azefhizeoghirgeoirhg",
            "password2": "azefhizeoghirgeoirhg",
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "This email domain is not allowed for registration.", form.errors["email"]
        )

        settings.WHITELIST_EMAIL_DOMAINS = ["authorized.com"]

        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid())
