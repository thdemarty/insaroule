from celery import shared_task

from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import EmailMessage


@shared_task
def send_verification_email(
    user_username, user_pk, user_email, user_token, site_base_url: str
):
    subject = "[INSAROULE] - Vérification de votre adresse email"
    message = render_to_string(
        "registration/verify_email/emails/verify_email.html",
        {
            "user": user_username,
            "domain": site_base_url,
            "uid": urlsafe_base64_encode(force_bytes(user_pk)),
            "token": user_token,
        },
    )
    email = EmailMessage(subject, message, to=[user_email])
    email.send()

    return f"Verification email sent to {user_email} for user {user_username} with ID {user_pk}."


@shared_task
def send_password_reset_email(
    subject_template_name,
    email_template_name,
    context,
    from_email,
    to_email,
    html_email_template_name,
):
    context["user"] = get_user_model().objects.get(pk=context["user"])

    PasswordResetForm.send_mail(
        None,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name,
    )
