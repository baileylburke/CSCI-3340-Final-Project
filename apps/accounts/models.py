from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """Our custom user model."""

    # Name that will be displayed around the website.
    display_name = models.CharField(max_length=150, blank=True)

    # Last time we saw this user make a request. Updated by
    # LastSeenMiddleware and used for the online/away presence dots.
    last_seen = models.DateTimeField(null=True, blank=True)

    # Controls how the user is represented when Django displays them.
    def __str__(self):
        return self.display_name or self.username

    @property
    def presence(self):
        """Return 'online', 'away', or 'offline' based on recent activity."""
        if not self.last_seen:
            return "offline"
        gap = timezone.now() - self.last_seen
        if gap < timedelta(minutes=5):
            return "online"
        if gap < timedelta(minutes=30):
            return "away"
        return "offline"

    def friends(self):
        """Everyone connected to this user by an accepted friend request."""
        sent = FriendRequest.objects.filter(
            from_user=self, accepted=True
        ).values_list("to_user", flat=True)
        received = FriendRequest.objects.filter(
            to_user=self, accepted=True
        ).values_list("from_user", flat=True)
        return User.objects.filter(id__in=list(sent) + list(received))

    def is_friends_with(self, other):
        """True if an accepted friend request links the two users."""
        return FriendRequest.objects.filter(
            models.Q(from_user=self, to_user=other)
            | models.Q(from_user=other, to_user=self),
            accepted=True,
        ).exists()


class FriendRequest(models.Model):
    # The person sending the friend request.
    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_friend_requests",
    )

    # The person receiving the friend request.
    to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_friend_requests",
    )

    # False = request is waiting.
    # True = the recipient accepted the request.
    accepted = models.BooleanField(default=False)

    # Automatically records when the request was created.
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Stops the same person sending the same request twice.
        constraints = [
            models.UniqueConstraint(
                fields=["from_user", "to_user"],
                name="unique_friend_request",
            ),
        ]

    # Makes the request readable when Django displays it.
    def __str__(self):
        return f"{self.from_user.username} -> {self.to_user.username}"
