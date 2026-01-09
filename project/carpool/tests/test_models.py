from django.test import TestCase

from carpool.tests.factories import RideFactory
from accounts.tests.factories import UserFactory


class ModelTestCase(TestCase):
    def test_remaining_seats(self):
        driver = UserFactory()
        ride = RideFactory(seats_offered=4, driver=driver)
        self.assertEqual(ride.remaining_seats, 4)
        user = UserFactory()
        ride.rider.add(user)
        self.assertEqual(ride.remaining_seats, 3)

    def test_is_full_property_when_ride_has_available_seats(self):
        driver = UserFactory()
        ride = RideFactory(seats_offered=3, driver=driver)
        
        user1 = UserFactory()
        ride.rider.add(user1)
        
        self.assertEqual(ride.remaining_seats, 2)
        self.assertFalse(ride.is_full)

    def test_is_full_property_when_ride_is_exactly_full(self):
        driver = UserFactory()
        ride = RideFactory(seats_offered=2, driver=driver)
        
        user1 = UserFactory()
        user2 = UserFactory()
        ride.rider.add(user1)
        ride.rider.add(user2)
        
        self.assertEqual(ride.remaining_seats, 0)
        self.assertTrue(ride.is_full)
