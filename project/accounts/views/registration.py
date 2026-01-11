from django.shortcuts import redirect
from django.contrib.auth.views import LoginView as BaseLoginView
from accounts.models import MultiFactorAuthenticationPolicy as MFAPolicy

import logging


class CustomLoginView(BaseLoginView):
    """
    Custom login view that sets a language cookie upon successful login.
    and also handle the MFA process for users who have it enabled.
    """

    def form_valid(self, form):
        user = form.get_user()

        if self.requires_mfa(user):
            self.request.session["pre_mfa_user_pk"] = str(user.pk)
            self.request.session["mfa_verified"] = False
            self.request.session["next"] = self.get_success_url()
            return redirect("accounts:mfa_totp_challenge")

        response = super().form_valid(form)

        if hasattr(self.request, "set_lang_cookie"):
            response = self.request.set_lang_cookie(response)

        return response

    def requires_mfa(self, user):
        """Check if the user requires MFA based on the policy."""
        policy = MFAPolicy.objects.first()

        if not policy:
            logging.critical("MFA Policy not created/ Please create one now.")
            return False

        user_in_enforced_users = policy.enforced_users.filter(pk=user.pk).exists()
        user_in_enforced_groups = policy.enforced_groups.filter(user=user).exists()

        requires_mfa = user_in_enforced_users or user_in_enforced_groups

        return requires_mfa
