from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def devices_list(request):
    """List all MFA devices for the logged-in user."""
    context = {}
    return render(request, "account/mfa/devices_list.html", context)


@login_required
def devices_add(request):
    """Add a new MFA device for the user."""
    context = {}
    return render(request, "account/mfa/devices_add.html", context)
