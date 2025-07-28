import factory

from django.utils import timezone

from chat.models import ChatRequest


class ChatRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ChatRequest

    user = factory.SubFactory("users.tests.factories.UserFactory")
    ride = factory.SubFactory("carpool.tests.factories.RideFactory")
    created_at = timezone.now()
