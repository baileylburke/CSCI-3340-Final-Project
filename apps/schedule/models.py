from django.conf import settings
from django.db import models


class Event(models.Model):
    """A calendar event, optionally tied to a project."""

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Optional project this event belongs to. Project members see it.
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="events",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="events",
    )

    starts_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["starts_at"]

    def __str__(self):
        return self.title
