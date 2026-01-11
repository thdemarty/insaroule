from django.test import TestCase
from accounts.models import MultiFactorAuthenticationPolicy as MFAPolicy
from accounts.tests.factories import UserFactory, GroupFactory

from django.urls import reverse


class MFATestCase(TestCase):
    def setUp(self):
        # Users in enforced group with and without devices
        self.enforced_mfa_group = GroupFactory(name="mfa_enforced_group")
        self.user1_without = UserFactory(
            email_verified=True, groups=[self.enforced_mfa_group], has_mfa=False
        )
        self.user2_with = UserFactory(
            email_verified=True, groups=[self.enforced_mfa_group], has_mfa=True
        )

        # Users in enforced users with and without devices
        self.user3_without = UserFactory(email_verified=True, has_mfa=False)
        self.user4_with = UserFactory(email_verified=True, has_mfa=True)

        # Staff user with and without devices
        self.staff_user_without = UserFactory(
            email_verified=True, is_staff=True, has_mfa=False
        )
        self.staff_user_with = UserFactory(
            email_verified=True, is_staff=True, has_mfa=True
        )

        # Superuser with and without devices
        self.superuser_without = UserFactory(
            email_verified=True, is_superuser=True, has_mfa=False
        )
        self.superuser_with = UserFactory(
            email_verified=True, is_superuser=True, has_mfa=True
        )

        # a regular user without MFA
        self.regular_user = UserFactory(email_verified=True, has_mfa=False)

        self.policy = MFAPolicy.objects.create()

    def test_mfa_no_policy(self):
        # Test logic for no MFA policy\
        pass

    def test_mfa_enforced_groups(self):
        # Test logic for MFA enforced groups
        # user1_with should be redirected to MFA challenge
        # user2_without should login normally
        self.policy.enforced_groups.add(self.enforced_mfa_group)

        self.client.force_login(self.user2_with)
        response = self.client.get(reverse("accounts:me"))

        self.client.logout()

        self.client.force_login(self.user1_without)
        response = self.client.get(reverse("accounts:me"))
        self.client.logout()

        print(response.request)

    def test_mfa_enforced_users(self):
        # Test logic for MFA enforced users
        pass

    def test_mfa_emforced_groups_without_devices(self):
        # Test logic for MFA enforced groups without devices
        pass

    def test_mfa_emforced_users_without_devices(self):
        # Test logic for MFA enforced users without devices
        pass

    def test_mfa_enforced_staff(self):
        # Test logic for MFA enforced staff
        pass

    def test_mfa_enforced_superusers(self):
        # Test logic for MFA enforced superusers
        pass
