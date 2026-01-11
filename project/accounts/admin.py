from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from accounts.models import (
    User,
    UserNotificationPreferences,
    MultiFactorAuthenticationDevice,
    MultiFactorAuthenticationPolicy,
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Extends the BaseUserAdmin by adding the score fields
    list_display = BaseUserAdmin.list_display + ("email_verified",)
    list_filter = BaseUserAdmin.list_filter + ("email_verified",)
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            _("Email verification"),
            {"fields": ("email_verified", "last_verification_email_sent")},
        ),
        (
            _("Preferences"),
            {"fields": ("preferred_language",)},
        ),
    )


@admin.register(UserNotificationPreferences)
class UserNotificationPreferencesAdmin(admin.ModelAdmin):
    pass


@admin.register(MultiFactorAuthenticationDevice)
class MultiFactorAuthenticationDeviceAdmin(admin.ModelAdmin):
    pass


@admin.register(MultiFactorAuthenticationPolicy)
class MultiFactorAuthenticationPolicyAdmin(admin.ModelAdmin):
    """singleton admin model for MFA policy"""

    def has_add_permission(self, request):
        if MultiFactorAuthenticationPolicy.objects.exists():
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the singleton instance
        return False
