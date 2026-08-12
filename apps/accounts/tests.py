from django.test import TestCase
from django.urls import reverse

from .models import User


class RegisterViewTests(TestCase):
    def valid_payload(self, **overrides):
        payload = {
            "display_name": "Alfred Z.",
            "username": "alfred",
            "email": "alfred@example.test",
            "password1": "correct-horse-battery",
            "password2": "correct-horse-battery",
        }
        payload.update(overrides)
        return payload

    def test_valid_signup_creates_the_user(self):
        response = self.client.post(reverse("accounts:register"), self.valid_payload())

        self.assertRedirects(response, reverse("accounts:login"))
        user = User.objects.get(username="alfred")
        self.assertEqual(user.display_name, "Alfred Z.")
        self.assertTrue(user.check_password("correct-horse-battery"))

    def test_weak_password_is_rejected(self):
        response = self.client.post(
            reverse("accounts:register"),
            self.valid_payload(password1="x", password2="x"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="alfred").exists())
        self.assertContains(response, "too short")

    def test_mismatched_passwords_are_rejected(self):
        response = self.client.post(
            reverse("accounts:register"),
            self.valid_payload(password2="something-else"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="alfred").exists())

    def test_duplicate_email_is_rejected(self):
        User.objects.create_user(
            username="someone", email="alfred@example.test", password="unrelated-pw-99"
        )

        response = self.client.post(reverse("accounts:register"), self.valid_payload())

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="alfred").exists())
        self.assertContains(response, "email already exists")

    def test_duplicate_username_is_rejected(self):
        User.objects.create_user(username="alfred", password="unrelated-pw-99")

        response = self.client.post(reverse("accounts:register"), self.valid_payload())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username="alfred").count(), 1)

    def test_missing_fields_render_errors_instead_of_500(self):
        response = self.client.post(reverse("accounts:register"), {})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)


class LoginViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="alfred", password="correct-horse-battery", display_name="Alfred Z."
        )

    def test_valid_login_starts_a_session(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "alfred", "password": "correct-horse-battery"},
        )

        self.assertRedirects(response, reverse("core:index"))
        self.assertEqual(self.client.session["_auth_user_id"], str(self.user.pk))

    def test_bad_password_shows_an_error(self):
        response = self.client.post(
            reverse("accounts:login"), {"username": "alfred", "password": "wrong"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_missing_fields_render_errors_instead_of_500(self):
        response = self.client.post(reverse("accounts:login"), {})

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)


class LogoutViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="alfred", password="correct-horse-battery"
        )
        self.client.force_login(self.user)

    def test_post_logs_the_user_out(self):
        response = self.client.post(reverse("accounts:logout"))

        self.assertRedirects(response, reverse("core:index"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_get_is_rejected_and_leaves_the_session_intact(self):
        response = self.client.get(reverse("accounts:logout"))

        self.assertEqual(response.status_code, 405)
        self.assertEqual(self.client.session["_auth_user_id"], str(self.user.pk))


class HomePageTests(TestCase):
    def test_greets_the_user_by_display_name(self):
        user = User.objects.create_user(
            username="alfred", password="correct-horse-battery", display_name="Alfred Z."
        )
        self.client.force_login(user)

        self.assertContains(self.client.get(reverse("core:index")), "Alfred Z.")

    def test_falls_back_to_username_when_no_display_name(self):
        user = User.objects.create_user(
            username="alfred", password="correct-horse-battery"
        )
        self.client.force_login(user)

        self.assertContains(self.client.get(reverse("core:index")), "alfred")
