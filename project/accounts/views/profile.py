from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _

from accounts.forms import EmailChangeForm
from accounts.tasks import send_email_export_data


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
            # set user's email verified to False
            request.user.save()
            messages.success(
                request,
                _("Your email has been changed. Please verify your new email address."),
            )
            return redirect("accounts:me")
    context = {"form": form}
    return render(request, "account/email_change.html", context)


@login_required
def export(request):
    # Get all the rides for which the user is the driver
    # or has subscribed to
    rides_as_driver = request.user.rides_as_driver.all()
    rides_as_rider = request.user.rides_as_rider.all()

    rides = rides_as_driver | rides_as_rider
    rides = rides.order_by("-start_dt")
    rides = [(ride.driver == request.user, ride) for ride in rides]

    if request.method == "POST":
        # Trigger the task to send the email with the data export
        send_email_export_data.delay(request.user.pk)
        return redirect("accounts:me")

    # Get all the rides for which the user is the driver
    context = {
        "rides": rides,
    }
    return render(request, "account/data_export.html", context)
