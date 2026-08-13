from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone


class LastSeenMiddleware:
    """Stamps request.user.last_seen so the online/away dots work.

    Only writes to the database at most once a minute per user, so we
    are not running an extra UPDATE on every single request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if user.is_authenticated:
            now = timezone.now()
            if user.last_seen is None or now - user.last_seen > timedelta(seconds=60):
                get_user_model().objects.filter(pk=user.pk).update(
                    last_seen=now
                )
        return self.get_response(request)
