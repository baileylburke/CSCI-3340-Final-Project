from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Our custom user model."""

    # Name that will be displayed around the website.
    display_name = models.CharField(max_length=150, blank=True)

    # Controls how the user is represented when Django displays them.
    def __str__(self):
        return self.display_name or self.username


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

    # Makes the request readable when Django displays it.
    def __str__(self):
        return f"{self.from_user.username} -> {self.to_user.username}"