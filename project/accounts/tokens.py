from django.contrib.auth.tokens import PasswordResetTokenGenerator


class EmailVerifyTokenGenerator(PasswordResetTokenGenerator):
    """Token generator for email verification"""

    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(timestamp) + str(user.email_verified)


email_verify_token = EmailVerifyTokenGenerator()
