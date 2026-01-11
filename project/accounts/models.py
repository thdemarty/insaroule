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
    preferred_language = models.CharField(
        max_length=10,
        choices=settings.LANGUAGES,
        default=settings.LANGUAGE_CODE,
        help_text=_("Preferred language for the user interface."),
    )

    @property
    def has_email_verify_cooldown(self):
        from datetime import timedelta

        from django.utils import timezone

        cooldown = timedelta(seconds=settings.COOLDOWN_EMAIL_VERIFY)
        if self.last_verification_email_sent:
            return timezone.now() - self.last_verification_email_sent < cooldown
        return False


class UserNotificationPreferences(models.Model):
    class Meta:
        verbose_name = "User notification preferences"
        verbose_name_plural = "User notification preferences"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="notification_preferences",
    )
    unread_messages_notification = models.BooleanField(
        default=True, help_text="Receive notifications for unread messages."
    )
    ride_status_update_notification = models.BooleanField(
        default=True, help_text="Receive notifications for ride status updates."
    )

    ride_sharing_suggestion_notification = models.BooleanField(
        default=True, help_text="Receive notifications suggesting to share rides."
    )


class MultiFactorAuthenticationDevice(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Device name"))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mfa_devices")
    totp_secret = models.CharField(max_length=32, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)


class MultiFactorAuthenticationPolicy(models.Model):
    """Singleton model to define MFA enforcement policies."""

    class Meta:
        verbose_name = "Multi-Factor Authentication Policy"
        verbose_name_plural = "Multi-Factor Authentication Policy"

    enforced_groups = models.ManyToManyField("auth.Group", blank=True)
    enforced_users = models.ManyToManyField(User, blank=True)
    enforced_for_staff = models.BooleanField(
        default=False,
        help_text="Enforce MFA for all staff users.",
    )
    enforced_for_superusers = models.BooleanField(
        default=True,
        help_text="Enforce MFA for all superuser accounts.",
    )

    def save(self, *args, **kwargs):
        """Ensure only one instance exists."""
        self.pk = 1
        super().save(*args, **kwargs)
