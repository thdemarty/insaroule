from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    REQUIRED_FIELDS = ["email", "email_verified"]

    uuid = models.UUIDField(
        _("UUID"),
        default=uuid4,
        unique=True,
        primary_key=True,
        editable=False,
    )

    email = models.EmailField(_("Email Address"), unique=True)
    email_verified = models.BooleanField(default=False)
    last_verification_email_sent = models.DateTimeField(null=True, blank=True)

    @property
    def has_email_verify_cooldown(self):
        from datetime import timedelta

        from django.utils import timezone

        cooldown = timedelta(seconds=settings.COOLDOWN_EMAIL_VERIFY)
        if self.last_verification_email_sent:
            return timezone.now() - self.last_verification_email_sent < cooldown
        return False
