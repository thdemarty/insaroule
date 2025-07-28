from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import Permission

from accounts.tests.factories import UserFactory
from carpool.tests.factories import RideFactory
from chat.tests.factories import ChatRequestFactory


class ParticipantChatViewTest(TestCase):
    def setUp(self):
        # Create two participants for the chat
        self.user1 = UserFactory(email_verified=True)
        self.user2 = UserFactory(email_verified=True)
        self.user3 = UserFactory(email_verified=True)
        # Create a ride and a chat request
        self.ride = RideFactory(driver=self.user1)

    def test_access_only_to_logged_in_users(self):
        """Test that the chat room can only be accessed by logged-in users."""
        pass

    def test_access_can_only_be_by_participants(self):
        """Test that only participants can access the chat room."""
        # Chat room between user1 (driver of the ride) and user2
        chat_request = ChatRequestFactory(ride=self.ride, user=self.user2)

        # User1 should be able to access the chat room
        self.client.force_login(self.user1)
        r = self.client.get(reverse("chat:room", kwargs={"jr_pk": chat_request.pk}))
        self.assertEqual(r.status_code, 200)

        # User2 should be able to access the chat room
        self.client.force_login(self.user2)
        r = self.client.get(reverse("chat:room", kwargs={"jr_pk": chat_request.pk}))
        self.assertEqual(r.status_code, 200)

        # User3 should not be able to access the chat room
        self.client.force_login(self.user3)
        r = self.client.get(reverse("chat:room", kwargs={"jr_pk": chat_request.pk}))
        self.assertEqual(r.status_code, 403)

    def test_report_can_only_be_by_one_of_participants(self):
        """Test that a report can only be made by one of the participants in the chat."""
        chat_request = ChatRequestFactory(ride=self.ride, user=self.user2)

        self.client.force_login(self.user1)
        self.client.post(
            reverse("chat:report", kwargs={"jr_pk": chat_request.pk}),
            data={"reason": "A reason"},
        )
        # Assert that their is a ChatReport created
        self.assertEqual(chat_request.reports.count(), 1)

        # Now try to report as the other participant
        self.client.force_login(self.user2)
        self.client.post(
            reverse("chat:report", kwargs={"jr_pk": chat_request.pk}),
            data={"reason": "A reason"},
        )
        # Assert that a report was created
        self.assertEqual(chat_request.reports.count(), 2)

        # Now try to report as a non-participant
        self.client.force_login(self.user3)
        self.client.post(
            reverse("chat:report", kwargs={"jr_pk": chat_request.pk}),
            data={"reason": "A reason"},
        )

        # Assert that no additional report was created (should still be 2)
        self.assertEqual(chat_request.reports.count(), 2)

    def test_user_can_not_access_mod_center(self):
        """Test that a regular user cannot access the mod center."""
        self.client.force_login(self.user1)
        r = self.client.get(reverse("chat:mod_index"))
        self.assertEqual(r.status_code, 403)

    def test_chat_index(self):
        """Test that the chat index shows the user's outgoing and incoming requests."""
        self.client.force_login(self.user1)
        r = self.client.get(reverse("chat:index"))
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, "chat/index.html")

        # Check that the context contains the user's outgoing and incoming requests
        self.assertIn("outgoing_requests", r.context)
        self.assertIn("incoming_requests", r.context)

        # TODO test with actual ChatRequest objects in the context


class ModeratorChatViewTest(TestCase):
    def setUp(self):
        # Create a moderator user and two regular users
        self.mod = UserFactory(email_verified=True)
        mod_perm = Permission.objects.get(codename="can_moderate_messages")
        self.mod.user_permissions.add(mod_perm)

        # Create two regular users that communicate together
        self.user1 = UserFactory(email_verified=True)
        self.user2 = UserFactory(email_verified=True)
        self.ride = RideFactory(driver=self.user1)

    def test_only_mods_can_add_user_reports(self):
        """Test that only moderators can report a user."""
        chat_request = ChatRequestFactory(ride=self.ride, user=self.user2)

        # Regular user should not be able to report
        self.client.force_login(self.user1)
        r = self.client.post(
            reverse("chat:user_report", kwargs={"user_pk": self.user2.pk}),
            data={
                "join_request_id": chat_request.pk,
                "reason": "Inappropriate behavior",
            },
        )
        self.assertEqual(r.status_code, 403)

        # Moderator should be able to report (redirects to the mod_room)
        self.client.force_login(self.mod)
        r = self.client.post(
            reverse("chat:user_report", kwargs={"user_pk": self.user2.pk}),
            data={
                "join_request_id": chat_request.pk,
                "reason": "Inappropriate behavior",
            },
        )
        self.assertRedirects(
            r, reverse("chat:mod_room", kwargs={"jr_pk": chat_request.pk})
        )

        # Asserts that a ModAction has been created
        self.assertEqual(self.user2.mod_actions_on_user.count(), 1)

    def test_hide_message(self):
        """Test hide message permissions and behavior."""
        chat_request = ChatRequestFactory(ride=self.ride, user=self.user2)
        message = chat_request.messages.create(
            content="Test message", sender=self.user1
        )

        # Regular user should not be able to hide the message
        self.client.force_login(self.user1)
        r = self.client.get(reverse("chat:hide_message", kwargs={"id": message.pk}))
        self.assertEqual(r.status_code, 403)

        # Moderator should be able to hide the message
        self.client.force_login(self.mod)
        r = self.client.get(reverse("chat:hide_message", kwargs={"id": message.pk}))
        self.assertEqual(r.status_code, 200)

        # Assert that the message is hidden
        message.refresh_from_db()
        self.assertTrue(message.hidden)

    def test_unhide_message(self):
        """Test unhide message permissions and behavior."""
        chat_request = ChatRequestFactory(ride=self.ride, user=self.user2)
        message = chat_request.messages.create(
            content="Test message", sender=self.user1, hidden=True
        )

        # Regular user should not be able to unhide the message
        self.client.force_login(self.user1)
        r = self.client.get(reverse("chat:unhide_message", kwargs={"id": message.pk}))
        self.assertEqual(r.status_code, 403)

        # Moderator should be able to unhide the message
        self.client.force_login(self.mod)
        r = self.client.get(reverse("chat:unhide_message", kwargs={"id": message.pk}))
        self.assertEqual(r.status_code, 200)

        # Assert that the message is no longer hidden
        message.refresh_from_db()
        self.assertFalse(message.hidden)

    def test_mod_index(self):
        """Test that the mod index is accessible only to moderators."""
        self.client.force_login(self.mod)
        r = self.client.get(reverse("chat:mod_index"))
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, "chat/moderation/index.html")

        # Check that the context contains the necessary data
        self.assertIn("page_obj", r.context)

        # Regular user should not be able to access the mod index
        self.client.force_login(self.user1)
        r = self.client.get(reverse("chat:mod_index"))
        self.assertEqual(r.status_code, 403)

        # TODO: Test that the reported chats  apperas
