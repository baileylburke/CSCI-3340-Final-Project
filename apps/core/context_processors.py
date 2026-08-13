def sidebar(request):
    """Data every page's sidebar needs: DM list and unread badge count."""

    if not request.user.is_authenticated:
        return {}

    # Imported here to avoid circular imports at startup.
    from apps.chat.models import Room
    from apps.core.models import Notification

    dms = []
    dm_rooms = Room.objects.filter(
        is_dm=True, members=request.user
    ).prefetch_related("members")
    for room in dm_rooms:
        other = room.other_member(request.user)
        if other:
            dms.append({"room": room, "person": other})

    return {
        "sidebar_dms": dms,
        "unread_notifications": Notification.objects.filter(
            user=request.user, read=False
        ).count(),
    }
