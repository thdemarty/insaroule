import factory

from django.contrib.auth.models import Permission

from accounts.models import User


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
