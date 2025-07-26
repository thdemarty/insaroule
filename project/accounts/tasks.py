import json

from celery import shared_task
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext as _


@shared_task
def send_verification_email(
    user_username,
    user_pk,
    user_email,
    user_token,
    site_base_url: str,
):
    subject = "[INSAROULE] - " + _("Vérification de votre adresse email")
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


@shared_task(rate_limit="10/h")
def send_email_export_data(user_pk):
    from django.core import serializers

    # Prepare the data for user in a json-like format

    user = get_user_model().objects.get(pk=user_pk)
    rides_as_driver = user.rides_as_driver.all()
    rides_as_rider = user.rides_as_rider.all()
    rides = rides_as_driver | rides_as_rider
    rides = rides.order_by("-start_dt")

    serialized_users = serializers.serialize(
        "json",
        [user],
        fields=[
            "username",
            "email",
            "first_name",
            "last_name",
            "date_joined",
            "last_login",
            "email_verified",
            "is_active",
            "is_staff",
            "is_superuser",
        ],
        use_natural_primary_keys=True,
    )

    data = {
        "user": json.loads(serialized_users)[0]["fields"],
        "rides": {
            "as_driver": json.loads(
                serializers.serialize(
                    "json",
                    user.rides_as_driver.all(),
                    fields=[
                        "start_dt",
                        "end_dt",
                        "start_loc",
                        "end_loc",
                        "payment_method",
                        "price",
                        "comment",
                        "steps",
                    ],
                ),
            ),
            "as_rider": json.loads(
                serializers.serialize(
                    "json",
                    user.rides_as_rider.all(),
                    use_natural_primary_keys=True,
                ),
            ),
        },
    }

    data_json = json.dumps(data, indent=4, ensure_ascii=False)

    # Send the email with the data file attached to the email

    subject = "[INSAROULE] - " + _("Data export")
    message = render_to_string(
        "account/data_export_email.txt",
        {
            "user": user,
            "rides_count": rides.count(),
        },
    )

    email = EmailMessage(
        subject,
        message,
        to=[user.email],
    )
    email.attach(
        "data_export.json",
        data_json,
        "application/json",
    )

    email.send()
