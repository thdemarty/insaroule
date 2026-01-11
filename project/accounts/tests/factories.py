import factory

from django.contrib.auth.models import Permission
from django.contrib.auth.models import Group

from accounts.models import User
from accounts.models import MultiFactorAuthenticationDevice as MFADevice


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "password123")

    @factory.post_generation
    def is_mod(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        permission = Permission.objects.get(codename="can_moderate_messages")
        self.user_permissions.add(permission)

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        self.groups.set(extracted)

    @factory.post_generation
    def has_mfa(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        MFADevice.objects.create(
            name=f"{self.username}_mfa_device",
            user=self,
        )


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group

    name = factory.Sequence(lambda n: f"Group{n}")
