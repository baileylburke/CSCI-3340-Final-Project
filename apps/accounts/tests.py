from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import FriendRequest

User = get_user_model()


class AuthTests(TestCase):
    def test_register_then_login(self):
        response = self.client.post(
            "/register/",
            {
                "display_name": "New Person",
                "username": "newperson",
                "email": "new@example.com",
                "password": "strongpass123",
                "confirm_password": "strongpass123",
            },
        )
        self.assertRedirects(response, "/login/")
        self.assertTrue(
            self.client.login(username="newperson", password="strongpass123")
        )

    def test_register_rejects_mismatched_passwords(self):
        response = self.client.post(
            "/register/",
            {
                "display_name": "X",
                "username": "x",
                "email": "x@example.com",
                "password": "one",
                "confirm_password": "two",
            },
        )
        self.assertContains(response, "Passwords do not match.")
        self.assertFalse(User.objects.filter(username="x").exists())


class FriendRequestTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user("alice", password="pass12345")
        self.bob = User.objects.create_user("bob", password="pass12345")
        self.client.login(username="bob", password="pass12345")

    def send_request(self, target):
        return self.client.post("/people/", {"user_id": target.id})

    def test_send_friend_request(self):
        self.send_request(self.alice)
        self.assertEqual(
            FriendRequest.objects.filter(
                from_user=self.bob, to_user=self.alice
            ).count(),
            1,
        )

    def test_duplicate_requests_are_blocked(self):
        self.send_request(self.alice)
        self.send_request(self.alice)
        self.assertEqual(FriendRequest.objects.count(), 1)

    def test_reverse_duplicate_is_blocked(self):
        FriendRequest.objects.create(from_user=self.alice, to_user=self.bob)
        self.send_request(self.alice)
        self.assertEqual(FriendRequest.objects.count(), 1)

    def test_cannot_friend_yourself(self):
        self.send_request(self.bob)
        self.assertEqual(FriendRequest.objects.count(), 0)

    def test_accept_requires_post(self):
        fr = FriendRequest.objects.create(
            from_user=self.alice, to_user=self.bob
        )
        response = self.client.get(f"/friend-requests/{fr.id}/accept/")
        self.assertEqual(response.status_code, 405)

    def test_accept_marks_accepted_and_makes_friends(self):
        fr = FriendRequest.objects.create(
            from_user=self.alice, to_user=self.bob
        )
        self.client.post(f"/friend-requests/{fr.id}/accept/")
        fr.refresh_from_db()
        self.assertTrue(fr.accepted)
        self.assertTrue(self.bob.is_friends_with(self.alice))

    def test_only_recipient_can_accept(self):
        fr = FriendRequest.objects.create(
            from_user=self.bob, to_user=self.alice
        )
        # bob (the sender) tries to accept his own request.
        response = self.client.post(f"/friend-requests/{fr.id}/accept/")
        self.assertEqual(response.status_code, 404)

    def test_decline_deletes_request(self):
        fr = FriendRequest.objects.create(
            from_user=self.alice, to_user=self.bob
        )
        self.client.post(f"/friend-requests/{fr.id}/decline/")
        self.assertEqual(FriendRequest.objects.count(), 0)
