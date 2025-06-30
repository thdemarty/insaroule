import datetime
from django.shortcuts import render, redirect, get_object_or_404
from carpool.models import Ride, Location
from django.contrib.auth.decorators import login_required
from carpool.forms import CreateRideForm


@login_required
def rides_detail(request, pk):
    ride = get_object_or_404(Ride, pk=pk)
    context = {
        "ride": ride,
    }
    return render(request, "rides/detail.html", context)


@login_required
def rides_list(request):
    context = {
        "rides": Ride.objects.all(),
    }
    return render(request, "rides/list.html", context)


@login_required
def rides_create(request):
    form = CreateRideForm()
    if request.method == "POST":
        form = CreateRideForm(request.POST)
        if form.is_valid():
            # Caching the addresses fetched from the form
            start_loc = Location.objects.get_or_create(
                label=form.cleaned_data["departure_fullname"],
                lat=form.cleaned_data["departure_lat"],
                lng=form.cleaned_data["departure_lng"],
            )[0]
            end_loc = Location.objects.get_or_create(
                label=form.cleaned_data["arrival_fullname"],
                lat=form.cleaned_data["arrival_lat"],
                lng=form.cleaned_data["arrival_lng"],
            )[0]
            # TODO: Save the route geojson to display it on the detail page of the ride
            # Get the end_dt from the geojson

            ride = Ride.objects.create(
                driver=request.user,
                start_dt=form.cleaned_data["departure_datetime"],
                end_dt=form.cleaned_data["departure_datetime"]
                + datetime.timedelta(days=1),
                start_loc=start_loc,
                end_loc=end_loc,
                payment_method=form.cleaned_data["payment_method"],
                price=form.cleaned_data["price_per_seat"],
            )

            return redirect("carpool:detail", pk=ride.id)

    context = {
        "form": form,
        "payment_methods": Ride.PaymentMethod.choices,
    }
    return render(request, "rides/create.html", context)
