from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def me(request):
    context = {}
    return render(request, "account/detail.html", context)
