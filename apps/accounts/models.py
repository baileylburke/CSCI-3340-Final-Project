from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model.

    Defined up front because AUTH_USER_MODEL cannot be changed after the
    first migration without rebuilding the database. Add profile fields
    here as they are needed.
    """

    display_name = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return self.display_name or self.username
