import pyotp

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from accounts.models import User
from accounts.models import MultiFactorAuthenticationDevice as MFADevice
from accounts.forms import MFADeviceAddForm, TOTPForm

from django.contrib.auth import login as auth_login


def totp_challenge(request):
    """
    View that is shown to the user to enter their TOTP code for MFA verification.
    """
    form = TOTPForm()
    user_pk = request.session.get("pre_mfa_user_pk")

    if not user_pk:
        # No pre-MFA user in session, redirect to login
        return redirect("accounts:login")

    user = User.objects.get(pk=user_pk)

    if not user.mfa_devices.exists():
        # Check if user has any MFA devices
        return redirect("accounts:login")

    totp_device = user.mfa_devices.first()

    if request.method == "POST":
        form = TOTPForm(request.POST)

        if form.is_valid(totp_device.totp_secret):
            # Mark MFA as verified in session
            request.session["mfa_verified"] = True
            next_url = request.session.get("next") or "carpool:list"
            auth_login(request, user)
            messages.success(request, "MFA verification successful.")
            return redirect(next_url)

    context = {
        "form": form,
    }
    return render(request, "account/mfa/totp.html", context)


@login_required
def devices_list(request):
    """List all MFA devices for the logged-in user."""
    context = {}
    return render(request, "account/mfa/devices_list.html", context)


@login_required
def devices_add(request):
    """Add a new MFA device for the user."""
    form = MFADeviceAddForm()

    # Block adding more than one device for now (will be expanded later)
    existing_devices = MFADevice.objects.filter(user=request.user)
    if existing_devices.exists():
        messages.error(
            request, "You can only have one MFA device registered for the moment."
        )
        return redirect("accounts:mfa_devices_list")

    if request.method == "GET":
        # Generate a new TOTP secret for the user every time
        # they reload the add device page (but not on POST)
        totp_secret = pyotp.random_base32()
        request.session["mfa_totp_secret"] = totp_secret

    if request.method == "POST":
        if not request.session.get("mfa_totp_secret"):
            # Check if the TOTP secret is in session
            messages.error(
                request, "Session expired. Please try adding the device again."
            )
            return redirect("accounts:mfa_devices_add")

        form = MFADeviceAddForm(request.POST)

        totp_secret = request.session["mfa_totp_secret"]

        if form.is_valid(totp_secret):
            # Add the new MFA device to the user's account
            form.save(request.user, totp_secret)
            return redirect("accounts:mfa_devices_list")

    context = {
        "form": form,
        "totp_secret": totp_secret,
    }
    return render(request, "account/mfa/devices_add.html", context)


@login_required
def devices_delete(request, pk):
    """Delete an MFA device for the user."""
    user = request.user
    device = MFADevice.objects.filter(id=pk, user=user)

    if not device.exists():
        messages.error(request, "You don't have permission to delete this device.")
        return redirect("accounts:mfa_devices_list")

    device = device.first()
    totp = TOTPForm()

    if request.method == "POST":
        totp = TOTPForm(request.POST)
        if totp.is_valid(device.totp_secret):
            device.delete()
            messages.warning(request, "MFA device deleted successfully.")
            return redirect("accounts:mfa_devices_list")

    context = {
        "device": device,
        "form": totp,
    }
    return render(request, "account/mfa/devices_delete.html", context)
