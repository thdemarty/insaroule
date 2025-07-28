from django.test import TestCase
from django.utils import timezone

from accounts.tests.factories import UserFactory


class TestUser(TestCase):
    def test_email_verified_is_false_by_default(self):
        """Test that the email_verified field is false by default."""
        user = UserFactory()
        self.assertFalse(user.email_verified)

    def test_has_email_verify_cooldown(self):
        """Test the has_email_verify_cooldown property."""
        user = UserFactory()

        # Initially, the user should not have a cooldown
        user.last_verification_email_sent = None
        self.assertFalse(user.has_email_verify_cooldown)

        # Set a cooldown period and check again
        user.last_verification_email_sent = timezone.now()
        self.assertTrue(user.has_email_verify_cooldown)
