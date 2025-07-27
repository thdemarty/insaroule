from django.test import TestCase
from carpool.forms import CreateRideForm


class CreateRideFormTestCase(TestCase):
    def setUp(self):
        return super().setUp()

    def test_clean_price_without_payment(self):
        form_data = {
            "d_fulltext": "Test ride",
            "d_street": "123 Main St",
            "d_zipcode": "12345",
            "d_city": "Test City",
            "d_latitude": 12.34,
            "d_longitude": 56.78,
            "a_fulltext": "Destination",
            "a_street": "456 Elm St",
            "a_zipcode": "67890",
            "a_city": "Destination City",
            "a_latitude": 87.65,
            "a_longitude": 43.21,
            "r_geometry": "some_geometry",
            "r_duration": 3600.0,
            "departure_datetime": "2023-10-01T12:00",
            "seats": 4,
            "price_per_seat": 0.00,
            "payment_method": [],
        }
        form = CreateRideForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_clean_price_with_payment(self):
        form_data = {
            "seats": 4,
            "price_per_seat": 10.00,
            "payment_method": ["cash"],
        }
        form = CreateRideForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertNotIn("payment_method", form.errors)
