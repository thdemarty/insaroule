import json
import logging

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):
    # TODO: simplify the logic by using external functions for permission checks and message retrieval
    async def connect(self):
        from chat.models import ChatMessage, ChatRequest

        self.user = self.scope["user"]
        self.room_name = self.scope["url_route"]["kwargs"]["jr_pk"]
        self.room_group_name = f"chat_{self.room_name}"

        self.chat_request = await sync_to_async(ChatRequest.objects.filter)(
            pk=self.room_name,
        )

        if not await self.chat_request.aexists():
            logging.error(f"ChatRequest with pk {self.room_name} does not exist.")
            await self.close()
            return

        self.chat_request = await self.chat_request.afirst()

        is_participant = await sync_to_async(
            lambda: self.user
            in [self.chat_request.user, self.chat_request.ride.driver],
        )()

        is_moderator = await sync_to_async(self.user.has_perm)(
            "chat.can_moderate_messages",
        )

        if self.user.is_anonymous or (not is_participant and not is_moderator):
            logging.error(
                f"User {self.user.username} attempted to join chat room {self.room_name} without permission. (Anonymous: {self.user.is_anonymous}, "
                f"Participant: {is_participant}, Moderator: {is_moderator})",
            )
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Send previous messages with user UUIDs
        previous_messages = await sync_to_async(list)(
            ChatMessage.objects.filter(chat_request=self.chat_request)
            .select_related("sender")
            .order_by("timestamp")[:50]
            .values("pk", "sender__uuid", "content", "timestamp", "hidden"),
        )

        for message in previous_messages:
            # if user is not a moderator, hide the content of hidden messages
            if is_moderator:
                await self.send(
                    text_data=json.dumps(
                        {
                            "type": "chat.message",
                            "id": message["pk"],
                            "message": message["content"],
                            "timestamp": message["timestamp"].isoformat(),
                            "user_uuid": str(message["sender__uuid"]),
                            "hidden": message["hidden"],
                        },
                    ),
                )
            else:
                await self.send(
                    text_data=json.dumps(
                        {
                            "type": "chat.message",
                            "id": message["pk"],
                            "message": "This message has been removed."
                            if message["hidden"]
                            else message["content"],
                            "timestamp": message["timestamp"].isoformat(),
                            "user_uuid": str(message["sender__uuid"]),
                            "hidden": message["hidden"],
                        },
                    ),
                )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """Handle incoming messages from the WebSocket.
        This method processes the received message, saves it to the database,
        and broadcasts it to the chat room.
        """
        from chat.models import ChatMessage

        logging.debug(f"Received message: {text_data}")

        text_data = json.loads(text_data)
        if "message" in text_data:
            message = text_data["message"]
            timestamp = timezone.now()

            if len(message.strip()) > 1000:
                logging.warning(
                    f"User {self.user.username} attempted to send a message exceeding 1000 characters.",
                )
                return

            message = await ChatMessage.objects.acreate(
                chat_request=self.chat_request,
                sender=self.user,
                content=message,
                timestamp=timestamp,
            )

            # Broadcast the message with user UUID
            data = {
                "type": "chat.message",
                "message": message.content,
                "timestamp": timestamp.isoformat(),
                "user_uuid": str(message.sender.uuid),
                "message_id": message.id,
            }

            logging.debug(f"Broadcasting message: {data}")

            await self.channel_layer.group_send(self.room_group_name, data)

        elif "action" in text_data:
            action = text_data["action"]
            message_id = text_data.get("message_id")

            if action == "hide" and message_id:
                if not self.user.has_perm("chat.can_moderate_messages"):
                    logging.warning(
                        f"User {self.user.username} attempted to hide a message without permission.",
                    )
                    return
                # Hide the message
                _ = await sync_to_async(
                    ChatMessage.objects.filter(pk=message_id).update,
                )(hidden=True)

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "chat.action",
                        "action": "hide",
                        "message_id": message_id,
                    },
                )

            elif action == "unhide" and message_id:
                if not self.user.has_perm("chat.can_moderate_messages"):
                    logging.warning(
                        f"User {self.user.username} attempted to unhide a message without permission.",
                    )
                    return
                _ = await sync_to_async(
                    ChatMessage.objects.filter(pk=message_id).update,
                )(hidden=False)

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "chat.action",
                        "action": "unhide",
                        "message_id": message_id,
                    },
                )

            elif action == "mark_read":
                logging.debug(
                    f"User {self.user.username} is marking messages as read in chat {self.room_name}.",
                )
                # Mark all messages in this chat as read by the user

                chats = await sync_to_async(
                    ChatMessage.objects.filter(
                        chat_request=self.chat_request,
                        read_at__isnull=True,
                    )
                    .exclude(sender=self.user)
                    .update
                )(read_at=timezone.now())

                logging.debug(f"Marked {chats} messages as read.")

    async def chat_message(self, event):
        """Handler for type 'chat.message'."""
        message = event["message"]
        timestamp = event["timestamp"]
        user_uuid = event["user_uuid"]

        await self.send(
            text_data=json.dumps(
                {
                    "type": "chat.message",
                    "message_id": event.get("message_id"),
                    "message": message,
                    "timestamp": timestamp,
                    "user_uuid": user_uuid,
                },
            ),
        )

    async def chat_action(self, event):
        """Handle chat actions."""
        action = event["action"]

        if action in ["hide", "unhide"]:
            message_id = event["message_id"]

            await self.send(
                text_data=json.dumps(
                    {
                        "type": "chat.action",
                        "action": action,
                        "message_id": message_id,
                    },
                ),
            )
        if action == "mark_read":
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "chat.action",
                        "action": "mark_read",
                        "user_uuid": event["user_uuid"],
                    }
                )
            )
