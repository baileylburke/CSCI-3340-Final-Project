from django.conf import settings
from django.db import models


class Room(models.Model):
    """A chat room. Direct messages are just two-person rooms."""

    # Blank for direct messages; the UI shows the other person's name instead.
    name = models.CharField(max_length=120, blank=True)
    description = models.CharField(max_length=200, blank=True)

    # Optional link to the project this room is about.
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rooms",
    )

    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="rooms"
    )

    # True when this room is a private two-person conversation.
    is_dm = models.BooleanField(default=False)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_rooms",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return self.name or f"DM #{self.id}"

    def other_member(self, user):
        """For DMs: the member who isn't the given user."""
        return self.members.exclude(id=user.id).first()

    def display_name(self, user):
        """What to call this room in the UI for the given user."""
        if self.is_dm:
            other = self.other_member(user)
            return str(other) if other else "Direct Message"
        return self.name


class Message(models.Model):
    """One chat message inside a room."""

    room = models.ForeignKey(
        Room, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.sender.username}: {self.text[:40]}"
