from django.conf import settings
from django.db import models


class Project(models.Model):
    """A project that a group of users works on together."""

    STATUS_CHOICES = [
        ("planning", "Planning"),
        ("in_progress", "In Progress"),
        ("done", "Done"),
    ]

    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="planning"
    )
    due_date = models.DateField(null=True, blank=True)

    # Everyone working on the project, including the creator.
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="projects"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_projects",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def progress(self):
        """Percent of this project's tasks that are done (0 if no tasks)."""
        total = self.tasks.count()
        if total == 0:
            return 0
        done = self.tasks.filter(done=True).count()
        return int(done * 100 / total)


class Task(models.Model):
    """A single piece of work inside a project."""

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="tasks"
    )
    title = models.CharField(max_length=200)

    # Who the task is assigned to. Can be left unassigned.
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
    )
    due_date = models.DateField(null=True, blank=True)
    done = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Open tasks first, then by soonest due date.
        ordering = ["done", models.F("due_date").asc(nulls_last=True)]

    def __str__(self):
        return self.title
