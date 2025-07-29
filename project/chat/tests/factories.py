import factory

from django.utils import timezone

from chat.models import ChatRequest, ChatMessage


class ChatRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ChatRequest

    user = factory.SubFactory("accounts.tests.factories.UserFactory")
    ride = factory.SubFactory("carpool.tests.factories.RideFactory")
    created_at = timezone.now()


class ChatMessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ChatMessage

    chat_request = factory.SubFactory(ChatRequestFactory)
    content = factory.Sequence(lambda n: f"Message {n}")
    timestamp = timezone.now()
    hidden = False
