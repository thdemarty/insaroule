from django.test import TestCase

from accounts.tests.factories import UserFactory
from django.urls import reverse
from django.utils import timezone
from unittest.mock import patch


class TestEmailVerify(TestCase):
    """Test cases for email verification system."""

    def test_last_email_verification_sent(self):
        """Test that last_verification_email_sent is updated when an email is sent."""
        user = UserFactory(email_verified=False, last_verification_email_sent=None)
        self.client.force_login(user)
        self.client.post(reverse("accounts:verify_email_send_token"))
        user.refresh_from_db()
        self.assertIsNotNone(user.last_verification_email_sent)

    @patch("accounts.tasks.send_verification_email.delay")
    def test_send_verification_email(self, mock_send):
        """Test that the user can send email only if it has no cooldown."""
        user = UserFactory(email_verified=False)
        self.client.force_login(user)

        user.last_verification_email_sent = timezone.now()
        self.client.post(reverse("accounts:verify_email_send_token"))
        self.assertTrue(mock_send.called)

        # Simulate a user with a cooldown period
        user.last_verification_email_sent = timezone.now()
        self.client.post(reverse("accounts:verify_email_send_token"))
        self.assertEqual(
            mock_send.call_count, 1
        )  # Should not call again if cooldown is active
