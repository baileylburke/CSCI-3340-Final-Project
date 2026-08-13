from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.accounts.models import FriendRequest

from .models import Message, Room

User = get_user_model()


class ChatTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user("alice", password="pass12345")
        self.bob = User.objects.create_user("bob", password="pass12345")
        self.outsider = User.objects.create_user(
            "outsider", password="pass12345"
        )
        self.room = Room.objects.create(name="Dev Team", created_by=self.alice)
        self.room.members.add(self.alice, self.bob)

    def test_member_can_open_room(self):
        self.client.login(username="alice", password="pass12345")
        response = self.client.get(f"/chat/{self.room.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dev Team")

    def test_non_member_gets_404(self):
        self.client.login(username="outsider", password="pass12345")
        response = self.client.get(f"/chat/{self.room.id}/")
        self.assertEqual(response.status_code, 404)

    def test_member_can_send_message(self):
        self.client.login(username="alice", password="pass12345")
        self.client.post(
            f"/chat/{self.room.id}/send/", {"text": "hello team"}
        )
        self.assertEqual(self.room.messages.count(), 1)

    def test_non_member_cannot_send_message(self):
        self.client.login(username="outsider", password="pass12345")
        response = self.client.post(
            f"/chat/{self.room.id}/send/", {"text": "let me in"}
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.room.messages.count(), 0)

    def test_polling_returns_only_new_messages(self):
        first = Message.objects.create(
            room=self.room, sender=self.alice, text="first"
        )
        second = Message.objects.create(
            room=self.room, sender=self.bob, text="second"
        )
        self.client.login(username="alice", password="pass12345")
        response = self.client.get(
            f"/chat/{self.room.id}/messages/?after={first.id}"
        )
        data = response.json()
        self.assertEqual(len(data["messages"]), 1)
        self.assertEqual(data["messages"][0]["id"], second.id)
        self.assertEqual(data["messages"][0]["text"], "second")

    def test_dm_is_created_once_and_only_for_friends(self):
        self.client.login(username="alice", password="pass12345")

        # Not friends yet: no DM created.
        self.client.get(f"/chat/dm/{self.bob.id}/")
        self.assertEqual(Room.objects.filter(is_dm=True).count(), 0)

        # Once friends, the DM is created and then reused.
        FriendRequest.objects.create(
            from_user=self.alice, to_user=self.bob, accepted=True
        )
        self.client.get(f"/chat/dm/{self.bob.id}/")
        self.client.get(f"/chat/dm/{self.bob.id}/")
        self.assertEqual(Room.objects.filter(is_dm=True).count(), 1)
