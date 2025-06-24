from django.urls import path
from django.contrib.auth.views import LoginView, logout_then_login
from accounts.views import register
from accounts.views.verify_email import (
    verify_email_send_token,
    verify_email_sent,
    verify_email_confirm,
    verify_email_complete,
)

app_name = "accounts"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", logout_then_login, name="logout"),
    path("register/", register, name="register"),
]

# Email verification URLs
urlpatterns += [
    path("register/email/", verify_email_send_token, name="verify_email_send_token"),
    path("register/email/sent/", verify_email_sent, name="verify_email_sent"),
    path(
        "register/email/confirm/<uidb64>/<token>/",
        verify_email_confirm,
        name="verify_email_confirm",
    ),
    path(
        "register/email/complete/", verify_email_complete, name="verify_email_complete"
    ),
]
