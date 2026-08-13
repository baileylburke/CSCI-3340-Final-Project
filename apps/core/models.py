from django.conf import settings
from django.db import models


class Notification(models.Model):
    """A short alert shown in the notifications panel and the bell badge."""

    # Who the notification is for.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    # The message shown to the user.
    text = models.CharField(max_length=255)

    # Where clicking the notification should take the user.
    link = models.CharField(max_length=255, blank=True)

    # Whether the user has seen it yet.
    read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username}: {self.text}"


def notify(user, text, link=""):
    """Small helper so other apps can create notifications in one line."""
    Notification.objects.create(user=user, text=text, link=link)
