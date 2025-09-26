from accounts.tests.factories import UserFactory

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from carpool.tests.factories import RideFactory


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
