from django.shortcuts import render, redirect
from accounts.forms import ForgotUsernameForm
from accounts.tasks import send_forgot_username_email
from django.contrib.auth.views import LoginView as BaseLoginView


class CustomLoginView(BaseLoginView):
    def form_valid(self, form):
        response = super().form_valid(form)
        if hasattr(self.request, "set_lang_cookie"):
            response = self.request.set_lang_cookie(response)
        return response


def forgot_username(request):
    """Custom view to handle forgot username"""
    form = ForgotUsernameForm()
    if request.method == "POST":
        form = ForgotUsernameForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            send_forgot_username_email.delay(email)

        return redirect("accounts:forgot_username_done")

    context = {"form": form}
    return render(request, "registration/forgot_username/index.html", context)


def forgot_username_done(request):
    return render(request, "registration/forgot_username/done.html")
