from channels.testing import WebsocketCommunicator as WSCommunicator
from django.contrib.auth.models import AnonymousUser
from django.test import TransactionTestCase
from asgiref.sync import sync_to_async

from accounts.tests.factories import UserFactory
from carpool.tests.factories import RideFactory
from chat.consumers import ChatConsumer
from chat.tests.factories import ChatRequestFactory, ChatMessageFactory
from chat.models import ChatMessage

"""
TODO: Other tests to be added:
- Test that a user can send and receive messages in the chat.
- Test that previous messages are sent upon connection.
- Test that a moderator can see hidden messages.
- Test that a non-moderator sees a placeholder for hidden messages.
- Test that chat are stored correctly in the database.
- Test that actions like hiding messages work as expected.
"""

# TODO: add a function for when a user connect to the ws chat room
#   it gets all the messages on the connection instead of having
#   to set u1c.receive_json_from() three times to get all the messages on
#   the room. This will make the tests cleaner and easier to read.


class ChatConsumerTests(TransactionTestCase):
    def setUp(self):
        """Set up the test case"""
        self.mod = UserFactory(email_verified=True, is_mod=True)
        self.user1 = UserFactory(email_verified=True)
        self.user2 = UserFactory(email_verified=True)
        self.user3 = UserFactory(email_verified=True)
        self.ride = RideFactory(driver=self.user1)
        self.room = ChatRequestFactory(
            user=self.user2,
            ride=self.ride,
        )
        # Create a chat history for the room self.room
        self.c1 = ChatMessageFactory(sender=self.user1, chat_request=self.room)
        self.c2 = ChatMessageFactory(sender=self.user2, chat_request=self.room)
        self.c3 = ChatMessageFactory(
            sender=self.user1, chat_request=self.room, hidden=True
        )

    async def test_entering_a_room_with_no_chat_request(self):
        """Test that a user cannot enter a room with no chat request"""
        communicator = WSCommunicator(ChatConsumer.as_asgi(), "/chat/")
        communicator.scope["url_route"] = {
            "kwargs": {"jr_pk": 9999}  # Non-existent ChatRequest
        }
        communicator.scope["user"] = self.user1

        connected, _ = await communicator.connect()
        self.assertFalse(connected)

        await communicator.disconnect()

    async def test_only_mods_and_participant_can_connect(self):
        """Test that only mods and participants can connect to the chat room"""
        # user1 can connect
        communicator = WSCommunicator(ChatConsumer.as_asgi(), "/chat/")
        communicator.scope["url_route"] = {"kwargs": {"jr_pk": self.room.pk}}
        communicator.scope["user"] = self.user1
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()

        # user3 cannot connect (not a valid participant)
        communicator = WSCommunicator(ChatConsumer.as_asgi(), "/chat/")
        communicator.scope["url_route"] = {"kwargs": {"jr_pk": self.room.pk}}
        communicator.scope["user"] = self.user3
        connected, _ = await communicator.connect()
        self.assertFalse(connected)
        await communicator.disconnect()

        # mod can connect
        communicator = WSCommunicator(ChatConsumer.as_asgi(), "/chat/")
        communicator.scope["url_route"] = {"kwargs": {"jr_pk": self.room.pk}}
        communicator.scope["user"] = self.mod
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()

        # anonymous user cannot connect
        communicator = WSCommunicator(ChatConsumer.as_asgi(), "/chat/")
        communicator.scope["url_route"] = {"kwargs": {"jr_pk": self.room.pk}}
        communicator.scope["user"] = AnonymousUser()
        connected, _ = await communicator.connect()
        self.assertFalse(connected)
        await communicator.disconnect()

        # user2 can connect
        communicator = WSCommunicator(ChatConsumer.as_asgi(), "/chat/")
        communicator.scope["url_route"] = {"kwargs": {"jr_pk": self.room.pk}}
        communicator.scope["user"] = self.user2
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()

    async def test_fetching_previous_messages_as_participant(self):
        """
        Test that previous messages are fetched correctly for a participant.
        They should not see hidden messages.
        """
        communicator = WSCommunicator(ChatConsumer.as_asgi(), "/chat/")
        communicator.scope["url_route"] = {"kwargs": {"jr_pk": self.room.pk}}
        communicator.scope["user"] = self.user1
        await communicator.connect()

        msg = await communicator.receive_json_from()
        self.assertEqual(msg["type"], "chat.message")
        self.assertEqual(msg["message"], self.c1.content)
        self.assertEqual(msg["user_uuid"], str(self.c1.sender.uuid))
        self.assertEqual(msg["hidden"], self.c1.hidden)

        msg = await communicator.receive_json_from()
        self.assertEqual(msg["type"], "chat.message")
        self.assertEqual(msg["message"], self.c2.content)
        self.assertEqual(msg["user_uuid"], str(self.c2.sender.uuid))
        self.assertEqual(msg["hidden"], self.c2.hidden)

        msg = await communicator.receive_json_from()
        self.assertEqual(msg["type"], "chat.message")
        self.assertEqual(msg["message"], "This message has been removed.")
        self.assertEqual(msg["user_uuid"], str(self.c3.sender.uuid))
        self.assertEqual(msg["hidden"], self.c3.hidden)

        await communicator.disconnect()

    async def test_fetching_previous_messages_as_moderator(self):
        """
        Test that previous messages are fetched correctly for a moderator.
        They should see hidden messages.
        """
        communicator = WSCommunicator(ChatConsumer.as_asgi(), "/chat/")
        communicator.scope["url_route"] = {"kwargs": {"jr_pk": self.room.pk}}
        communicator.scope["user"] = self.mod
        await communicator.connect()

        msg = await communicator.receive_json_from()
        self.assertEqual(msg["type"], "chat.message")
        self.assertEqual(msg["message"], self.c1.content)
        self.assertEqual(msg["user_uuid"], str(self.c1.sender.uuid))
        self.assertEqual(msg["hidden"], self.c1.hidden)

        msg = await communicator.receive_json_from()
        self.assertEqual(msg["type"], "chat.message")
        self.assertEqual(msg["message"], self.c2.content)
        self.assertEqual(msg["user_uuid"], str(self.c2.sender.uuid))
        self.assertEqual(msg["hidden"], self.c2.hidden)

        msg = await communicator.receive_json_from()
        self.assertEqual(msg["type"], "chat.message")
        self.assertEqual(msg["message"], self.c3.content)
        self.assertEqual(msg["user_uuid"], str(self.c3.sender.uuid))
        self.assertEqual(msg["hidden"], self.c3.hidden)

        await communicator.disconnect()

    async def test_hiding_message_in_real_time(self):
        """Test that a moderator can hide a message in real-time."""
        mdc = WSCommunicator(ChatConsumer.as_asgi(), "/chat/")
        u1c = WSCommunicator(ChatConsumer.as_asgi(), "/chat/")
        mdc.scope["url_route"] = {"kwargs": {"jr_pk": self.room.pk}}
        u1c.scope["url_route"] = {"kwargs": {"jr_pk": self.room.pk}}
        mdc.scope["user"] = self.mod
        u1c.scope["user"] = self.user1

        # TODO simplify this by having a function that connects the user and receives all the messages
        await mdc.connect()
        await mdc.receive_json_from()
        await mdc.receive_json_from()
        await mdc.receive_json_from()

        await u1c.connect()
        await u1c.receive_json_from()
        await u1c.receive_json_from()
        await u1c.receive_json_from()

        # User send a message
        await u1c.send_json_to({"type": "chat.message", "message": "Censor me plz"})
        await u1c.receive_json_from()

        # Wait for the message to be received by the moderator
        msg = await mdc.receive_json_from()

        # Moderator send an action to hide the message
        await mdc.send_json_to(
            {
                "type": "chat.action",
                "action": "hide",
                "message_id": msg["message_id"],
            }
        )

        msg = await u1c.receive_json_from()

    async def test_unhiding_message_in_real_time(self):
        """Test that a moderator can unhide a message in real-time."""
        mdc = WSCommunicator(ChatConsumer.as_asgi(), "/chat/")
        u1c = WSCommunicator(ChatConsumer.as_asgi(), "/chat/")
        mdc.scope["url_route"] = {"kwargs": {"jr_pk": self.room.pk}}
        u1c.scope["url_route"] = {"kwargs": {"jr_pk": self.room.pk}}
        mdc.scope["user"] = self.mod
        u1c.scope["user"] = self.user1

        await mdc.connect()
        await mdc.receive_json_from()
        await mdc.receive_json_from()
        await mdc.receive_json_from()

        await u1c.connect()
        await u1c.receive_json_from()
        await u1c.receive_json_from()
        await u1c.receive_json_from()

        # User send a message
        await u1c.send_json_to({"type": "chat.message", "message": "Censor me plz"})
        msg = await u1c.receive_json_from()

        # Wait for the message to be received by the moderator
        msg = await mdc.receive_json_from()

        # Moderator send an action to hide the message
        await mdc.send_json_to(
            {
                "type": "chat.action",
                "action": "hide",
                "message_id": msg["message_id"],
            }
        )

        # Wait for the user to receive the hidden message
        msg = await u1c.receive_json_from()

        # Moderator send an action to unhide the message
        await mdc.send_json_to(
            {
                "type": "chat.action",
                "action": "unhide",
                "message_id": msg["message_id"],
            }
        )

        # Wait for the user to receive the unhidden message
        msg = await u1c.receive_json_from()

    async def test_regular_user_cannot_send_chat_actions(self):
        """Test that a regular user cannot send chat actions."""

        u1c = WSCommunicator(ChatConsumer.as_asgi(), "/chat/")
        u1c.scope["url_route"] = {"kwargs": {"jr_pk": self.room.pk}}
        u1c.scope["user"] = self.user1

        # TODO: simplify also this with a simple
        await u1c.connect()
        await u1c.receive_json_from()
        await u1c.receive_json_from()
        await u1c.receive_json_from()

        # Try to send an action
        await u1c.send_json_to(
            {
                "type": "chat.action",
                "action": "hide",
                "message_id": 12345,  # Arbitrary message ID
            }
        )

        # no response should be received, as the action should be ignored
        assert await u1c.receive_nothing()

        await u1c.disconnect()

    async def test_chat_storage(self):
        """Test that messages are stored correctly in the database."""

        u1c = WSCommunicator(ChatConsumer.as_asgi(), "/chat/")
        u2c = WSCommunicator(ChatConsumer.as_asgi(), "/chat/")
        u1c.scope["url_route"] = {"kwargs": {"jr_pk": self.room.pk}}
        u2c.scope["url_route"] = {"kwargs": {"jr_pk": self.room.pk}}
        u1c.scope["user"] = self.user1
        u2c.scope["user"] = self.user2
        await u1c.connect()
        await u1c.receive_json_from()
        await u1c.receive_json_from()
        await u1c.receive_json_from()

        await u2c.connect()
        await u2c.receive_json_from()
        await u2c.receive_json_from()
        await u2c.receive_json_from()

        # Send a new message as user1
        new_message = "Hello, this is a test message."
        await u1c.send_json_to({"type": "chat.message", "message": new_message})

        # Wait for user2 to receive the message
        # So we now it was stored in database
        await u1c.receive_json_from()

        # Check if the message was stored in the database
        res = await sync_to_async(ChatMessage.objects.filter)(content=new_message)
        self.assertTrue(
            await res.aexists(), "The message was not stored in the database."
        )

        await u1c.disconnect()
        await u2c.disconnect()
