from accounts.tests.factories import UserFactory

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from carpool.tests.factories import RideFactory, VehicleFactory
from carpool.models.reservation import Reservation
from chat.models import ChatRequest


class AnonymousAccessTestCase(TestCase):
    def setUp(self):
        u1 = UserFactory()
        self.r1 = RideFactory(driver=u1)
        self.r2 = RideFactory(driver=u1)

    def test_anonymous_access_rides_list(self):
        # Anonymous access to rides list is disabled
        settings.ANONYMOUS_ACCESS_RIDES_LIST = False
        r = self.client.get(reverse("carpool:list"))
        self.assertEqual(r.status_code, 302)
        self.assertIn(reverse("accounts:login"), r.url)

        # Anonymous access to rides list is enabled
        settings.ANONYMOUS_ACCESS_RIDES_LIST = True
        r = self.client.get(reverse("carpool:list"))
        self.assertEqual(r.status_code, 200)
        self.assertIn(self.r1, r.context["rides"])
        self.assertIn(self.r2, r.context["rides"])

    def test_login_required_map_view(self):
        # Test that rides map view requires login
        r = self.client.get(reverse("carpool:map"))
        self.assertEqual(r.status_code, 302)
        self.assertIn(reverse("accounts:login"), r.url)

    def test_login_required_ride_detail(self):
        # Test that ride detail view requires login
        r = self.client.get(reverse("carpool:detail", kwargs={"pk": self.r1.pk}))
        self.assertEqual(r.status_code, 302)
        self.assertIn(reverse("accounts:login"), r.url)

    def test_login_required_ride_subscribe(self):
        # Test that ride subscribe view requires login
        r = self.client.get(
            reverse("carpool:subscribe", kwargs={"ride_pk": self.r1.pk})
        )
        self.assertEqual(r.status_code, 302)
        self.assertIn(reverse("accounts:login"), r.url)

    def test_login_required_ride_edit(self):
        # Test that ride edit view requires login
        r = self.client.get(reverse("carpool:edit", kwargs={"pk": self.r1.pk}))
        self.assertEqual(r.status_code, 302)
        self.assertIn(reverse("accounts:login"), r.url)


class VehicleViewTestCase(TestCase):
    def setUp(self):
        self.user1 = UserFactory(email_verified=True)
        self.user2 = UserFactory(email_verified=True)
        self.vehicle1 = VehicleFactory(driver=self.user1)

    def test_vehicle_create_view(self):
        # Test only post method is allowed
        # Test that the vehicle is created and linked to the request user
        # Test the response is a json containing the vehicle data created
        # Test that invalid data returns the form with errors TODO better errors in the frontend
        pass

    def test_vehicle_update_view(self):
        self.client.force_login(self.user1)
        url = reverse("carpool:update_vehicle", kwargs={"pk": self.vehicle1.pk})

        # Test only post method is allowed
        r = self.client.get(url)
        self.assertEqual(r.status_code, 405)  # Method Not Allowed

        # Test editing a vehicle by its driver
        self.client.force_login(self.user1)
        r = self.client.post(
            url,
            {
                "name": "Updated Vehicle",
                "description": "Updated Description",
                "seats": 4,
                "geqCO2_per_km": 90.0,
            },
        )
        self.assertEqual(r.status_code, 201)

        # Test the vehicle data is invalid
        r = self.client.post(
            url,
            {
                "name": "",  # Name is required
                "description": "Updated Description",
                "seats": -1,  # Invalid seats
                "geqCO2_per_km": -50.0,  # Invalid geqCO2_per_km
            },
        )
        self.assertEqual(r.status_code, 400)
        self.assertIn("name", r.json()["errors"])
        self.assertIn("seats", r.json()["errors"])
        self.assertIn("geqCO2_per_km", r.json()["errors"])

        # Test that a user cannot edit another user's vehicle
        self.client.force_login(self.user2)
        r = self.client.post(
            url,
            {
                "name": "Malicious Update",
                "description": "Hacked Description",
                "seats": 2,
                "geqCO2_per_km": 150.0,
            },
        )
        self.assertEqual(r.status_code, 403)  # Forbidden
        self.assertIn("You are not the driver", r.json().get("error", ""))


class RideSubscriptionTestCase(TestCase):
    def setUp(self):
        self.driver = UserFactory(email_verified=True)
        self.passenger = UserFactory(email_verified=True)

    def test_cannot_book_full_ride(self):
        """Test that users cannot book a ride that is already full"""
        ride = RideFactory(seats_offered=1, driver=self.driver)
        
        user1 = UserFactory()
        ride.rider.add(user1)
        
        self.assertTrue(ride.is_full)
        self.assertEqual(ride.remaining_seats, 0)
        
        # Try to book the full ride as another user
        self.client.force_login(self.passenger)
        
        # Create a chat request (required for booking)
        chat_request = ChatRequest.objects.create(user=self.passenger, ride=ride)
        
        response = self.client.post(
            reverse("carpool:subscribe", kwargs={"ride_pk": ride.pk})
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("carpool:list"))
        
        # Check that no reservation was created
        self.assertFalse(
            Reservation.objects.filter(user=self.passenger, ride=ride).exists()
        )
        
        self.assertNotIn(self.passenger, ride.rider.all())

    def test_can_book_ride_with_available_seats(self):
        """Test that users can book a ride that has available seats"""
        ride = RideFactory(seats_offered=2, driver=self.driver)
        
        self.assertFalse(ride.is_full)
        self.assertEqual(ride.remaining_seats, 2)
        
        self.client.force_login(self.passenger)
        
        chat_request = ChatRequest.objects.create(user=self.passenger, ride=ride)
        
        response = self.client.post(
            reverse("carpool:subscribe", kwargs={"ride_pk": ride.pk})
        )

        # Should create a reservation
        self.assertTrue(
            Reservation.objects.filter(user=self.passenger, ride=ride).exists()
        )
    def test_cannot_accept_booking_when_full(self):
        ride = RideFactory(seats_offered=1, driver=self.driver)
                
        # Book the ride
        self.client.force_login(self.passenger)
        
        # Create a chat request (required for booking)
        chat_request = ChatRequest.objects.create(user=self.passenger, ride=ride)
        
        response = self.client.post(
            reverse("carpool:subscribe", kwargs={"ride_pk": ride.pk})
        )

        user1 = UserFactory()
        ride.rider.add(user1)

        # Ensure the ride is full
        self.assertTrue(ride.is_full)
        self.assertEqual(ride.remaining_seats, 0)

        self.client.force_login(self.driver)
                
        reservation = Reservation.objects.get(user=self.passenger, ride=ride)
        response = self.client.post(
            reverse("carpool:update_reservation"), 
            {"action": "accept", "reservation_pk": reservation.pk}
        )

        # Check that response indicates the ride is fully booked
        self.assertEqual(response.status_code, 409)
        self.assertIn("fully booked", response.content.decode())

        # Check that the reservation status is still PENDING
        Reservation.refresh_from_db(reservation)
        self.assertEqual(reservation.status, Reservation.Status.PENDING)

        # Check that the ride is still full
        self.assertEqual(ride.remaining_seats, 0)
        self.assertEqual(ride.rider.count(), 1)


        