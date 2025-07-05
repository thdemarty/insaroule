from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.forms import EmailChangeForm


@login_required
def user_profile(request):
    context = {}
    return render(request, "account/detail.html", context)


@login_required
def delete_profile(request):
    if request.method == "POST":
        user = request.user
        user.delete()
        return redirect("accounts:login")
    context = {}
    return render(request, "account/close.html", context)


@login_required
def email_change(request):
    form = EmailChangeForm()
    if request.method == "POST":
        form = EmailChangeForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            request.user.email = email
            request.user.save()

            return redirect("accounts:me")
    context = {"form": form}
    return render(request, "account/email_change.html", context)
