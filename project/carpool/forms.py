from django import forms
from carpool.models import Ride


class CreateRideForm(forms.Form):
    departure_fullname = forms.CharField(required=True, widget=forms.HiddenInput())
    departure_lat = forms.FloatField(required=True, widget=forms.HiddenInput())
    departure_lng = forms.FloatField(required=True, widget=forms.HiddenInput())
    arrival_fullname = forms.CharField(required=True, widget=forms.HiddenInput())
    arrival_lat = forms.FloatField(required=True, widget=forms.HiddenInput())
    arrival_lng = forms.FloatField(required=True, widget=forms.HiddenInput())
    route = forms.CharField(required=True, widget=forms.HiddenInput())

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
        min_value=0.01,
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
