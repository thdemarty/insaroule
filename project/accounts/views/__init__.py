from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import login
from accounts.forms import RegisterForm


def register(request):
    if settings.ALLOW_REGISTRATION:
        form = RegisterForm()
        if request.method == "POST":
            form = RegisterForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                return redirect("accounts:verify_email_send_token")
        context = {"form": form}
    else:
        context = {"not_allowed": True}
    return render(request, "registration/register.html", context)
