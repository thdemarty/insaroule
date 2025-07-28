from django.test import TestCase
from accounts.tests.factories import UserFactory
from django.urls import reverse


class MiddlewareTestCase(TestCase):
    def test_redirect_user_with_email_not_verified(self):
        """Test that authenticated users with unverified email are redirected."""
        user = UserFactory(email_verified=False)
        self.client.force_login(user)
        response = self.client.get("/")
        self.assertRedirects(response, reverse("accounts:verify_email_send_token"))

    def test_no_redirect_user_with_email_verified(self):
        """Test that authenticated users with verified email are not redirected."""
        user = UserFactory(email_verified=True)
        self.client.force_login(user)
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
