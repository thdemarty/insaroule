from django.shortcuts import redirect
from django.contrib.auth.views import LoginView as BaseLoginView


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
        # FIXME: Temporary condition for testing MFA, will be improved later
        condition = user.is_staff and user.mfa_devices.exists()
        return condition
