from django import forms
from django.utils import timezone
from carpool.models.ride import Ride


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
                "min": timezone.now().strftime("%Y-%m-%dT%H:%M"),
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
        required=False,
        choices=Ride.PaymentMethod.choices,
        widget=forms.CheckboxSelectMultiple,
    )

    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get("price_per_seat")
        payment = cleaned_data.get("payment_method")

        if price is not None and price > 0:
            if not payment:
                self.add_error(
                    "payment_method", "A payment method is required if a price is set."
                )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            widget = field.widget
            if field_name == "payment_method":
                if self.errors.get(field_name):
                    widget.attrs["class"] = "is-invalid"
                continue
            css_class = widget.attrs.get("class", "")
            if self.errors.get(field_name):
                widget.attrs["class"] = f"{css_class} is-invalid"
            else:
                widget.attrs.setdefault("class", "form-control")

        now = timezone.now().strftime("%Y-%m-%dT%H:%M")
        self.fields["departure_datetime"].widget.attrs["min"] = now
