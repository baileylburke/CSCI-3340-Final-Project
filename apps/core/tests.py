from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from .models import Notification, notify

User = get_user_model()


class PageTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user("alice", password="pass12345")

    def test_visitor_sees_landing_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Join Now")

    def test_logged_in_user_sees_dashboard(self):
        self.client.login(username="alice", password="pass12345")
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome back")
        self.assertContains(response, "Active Projects")

    def test_protected_pages_redirect_visitors_to_login(self):
        for url in [
            "/people/",
            "/friend-requests/",
            "/projects/",
            "/chat/",
            "/calendar/",
            "/notifications/",
        ]:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302, url)
            self.assertIn("/login/", response.url)

    def test_search_page(self):
        self.client.login(username="alice", password="pass12345")
        response = self.client.get("/search/?q=ali")
        self.assertEqual(response.status_code, 200)


class NotificationTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user("alice", password="pass12345")

    def test_visiting_page_marks_notifications_read(self):
        notify(self.alice, "Something happened.")
        self.client.login(username="alice", password="pass12345")

        self.assertEqual(
            Notification.objects.filter(user=self.alice, read=False).count(), 1
        )
        response = self.client.get("/notifications/")
        self.assertContains(response, "Something happened.")
        self.assertEqual(
            Notification.objects.filter(user=self.alice, read=False).count(), 0
        )


class SeedCommandTests(TestCase):
    def test_seed_demo_runs_and_is_idempotent(self):
        call_command("seed_demo", stdout=StringIO())
        call_command("seed_demo", stdout=StringIO())  # running twice is safe
        self.assertTrue(User.objects.filter(username="jason").exists())
        jason = User.objects.get(username="jason")
        self.assertGreater(jason.projects.count(), 0)
        self.assertGreater(jason.rooms.count(), 0)
