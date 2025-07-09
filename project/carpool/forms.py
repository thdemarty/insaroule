from django import forms
from carpool.models import Ride


class CreateRideForm(forms.Form):
    # Departure information
    d_fulltext = forms.CharField(required=True, widget=forms.HiddenInput())
    d_street = forms.CharField(
        required=False, widget=forms.HiddenInput()
    )  # Not necessary a street (could be a city)
    d_zipcode = forms.CharField(required=True, widget=forms.HiddenInput())
    d_city = forms.CharField(required=True, widget=forms.HiddenInput())
    d_latitude = forms.FloatField(required=True, widget=forms.HiddenInput())
    d_longitude = forms.FloatField(required=True, widget=forms.HiddenInput())

    # Arrival information
    a_fulltext = forms.CharField(required=True, widget=forms.HiddenInput())
    a_street = forms.CharField(
        required=False, widget=forms.HiddenInput()
    )  # Not necessary a street (could be a city)
    a_zipcode = forms.CharField(required=True, widget=forms.HiddenInput())
    a_city = forms.CharField(required=True, widget=forms.HiddenInput())
    a_latitude = forms.FloatField(required=True, widget=forms.HiddenInput())
    a_longitude = forms.FloatField(required=True, widget=forms.HiddenInput())

    # Routing information
    r_geometry = forms.CharField(required=True, widget=forms.HiddenInput())
    r_duration = forms.FloatField(required=True, widget=forms.HiddenInput())

    departure_datetime = forms.DateTimeField(
        required=True,
        widget=forms.DateTimeInput(
            attrs={
                "type": "datetime-local",
                "class": "form-control",
            }
        ),
    )

    seats = forms.IntegerField(
        required=True,
        min_value=1,
        max_value=8,
        widget=forms.NumberInput(
            attrs={
                "placeholder": "Number of seats available",
                "class": "form-control",
            }
        ),
        help_text="Number of seats available in the carpool.",
    )

    price_per_seat = forms.DecimalField(
        required=True,
        min_value=0,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                "placeholder": "TODO Automatic price calculation",
                "class": "form-control",
            }
        ),
    )

    payment_method = forms.MultipleChoiceField(
        required=True,
        choices=Ride.PaymentMethod.choices,
        widget=forms.CheckboxSelectMultiple,
    )
