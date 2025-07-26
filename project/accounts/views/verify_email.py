from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.http import urlsafe_base64_decode

from accounts.tasks import send_verification_email
from accounts.tokens import email_verify_token

# ============================================================= #
#                   Email verification views                    #
# ============================================================= #
# Verify email send token  : send email to user with a link to verify their email
# verify email sent : confirm that the email has been sent
# Verify email confirm: confirm the email verification
# Verify email complete : redirect the user to the home page after email verification


@login_required
def verify_email_send_token(request):
    """
    Email verification view to send a token
    """
    if request.user.email_verified:
        print("User has already verified email, redirecting to carpool list")
        return redirect("carpool:list")

    if (
        request.user.last_verification_email_sent
        and request.user.has_email_verify_cooldown
    ):
        # Early return if the user has a cooldown
        print("Early return due to cooldown")
        return redirect("accounts:verify_email_sent")

    if request.method == "POST":
        # Send the verification email only if the user has no cooldown

        send_verification_email.delay(
            request.user.username,
            request.user.pk,
            request.user.email,
            email_verify_token.make_token(request.user),
            site_base_url=request.scheme + "://" + get_current_site(request).domain,
        )

        request.user.last_verification_email_sent = timezone.now()
        request.user.save(update_fields=["last_verification_email_sent"])

        return redirect("accounts:verify_email_sent")

    return render(request, "registration/verify_email/send_token.html")


@login_required()
def verify_email_sent(request):
    """
    When the email has been sent, redirect to this page. The user
    can request another email if the cooldown is over.
    """
    if request.user.email_verified:
        print("User has already verified email, redirecting to carpool list")
        return redirect("carpool:list")

    if (
        request.user.last_verification_email_sent
        and request.user.has_email_verify_cooldown
    ):
        # If the user has a cooldown, calculate the time remaining
        cooldown = timedelta(seconds=settings.COOLDOWN_EMAIL_VERIFY)
        not_before = request.user.last_verification_email_sent + cooldown
        minutes = (not_before - timezone.now()).total_seconds() / 60
        context = {
            "cooldown": True,
            "not_before": not_before,
            "minutes": int(minutes),
        }
    else:
        context = {
            "cooldown": False,
        }

    return render(request, "registration/verify_email/email_sent.html", context)


def verify_email_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    if user is not None and email_verify_token.check_token(user, token):
        user.email_verified = True
        user.active = True
        user.save()
        return redirect("accounts:verify_email_complete")
    else:
        messages.error(request, "Verification link is invalid")
    return render(request, "registration/verify_email/confirm.html")


def verify_email_complete(request):
    return render(request, "registration/verify_email/complete.html")
