from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone

from apps.schedule.services import build_month, events_for

User = get_user_model()


def index(request):
    """Landing page for visitors, dashboard for logged-in users."""

    if not request.user.is_authenticated:
        return render(request, "home.html")

    user = request.user
    today = timezone.localdate()
    now = timezone.now()

    # The user's projects drive most of the dashboard numbers.
    projects = user.projects.all()

    stats = {
        "active_projects": projects.exclude(status="done").count(),
        "teammates": (
            User.objects.filter(projects__in=projects)
            .exclude(id=user.id)
            .distinct()
            .count()
        ),
        "tasks_due_soon": user.tasks.filter(
            done=False, due_date__lte=today + timedelta(days=7)
        ).count(),
        "events_today": events_for(user)
        .filter(starts_at__date=today)
        .count(),
    }

    # Rooms panel: the user's team rooms, with one open in the chat pane.
    rooms = user.rooms.filter(is_dm=False)
    active_room = None
    room_id = request.GET.get("room")
    if room_id and room_id.isdigit():
        active_room = rooms.filter(id=room_id).first()
    if active_room is None:
        active_room = rooms.first()

    chat_messages = []
    if active_room:
        # Last 30 messages, oldest first for display.
        chat_messages = list(
            active_room.messages.select_related("sender").order_by(
                "-created_at"
            )[:30]
        )[::-1]

    return render(
        request,
        "core/dashboard.html",
        {
            "stats": stats,
            "rooms": rooms,
            "active_room": active_room,
            "chat_messages": chat_messages,
            "recent_projects": projects[:4],
            "calendar": build_month(user),
            "upcoming_events": events_for(user).filter(
                starts_at__gte=now
            )[:5],
            "recent_notifications": user.notifications.all()[:4],
        },
    )


@login_required
def search(request):
    """Topbar search across people, projects, and the user's rooms."""

    query = request.GET.get("q", "").strip()

    people = []
    projects = []
    rooms = []
    if query:
        people = User.objects.filter(
            Q(username__icontains=query) | Q(display_name__icontains=query)
        ).exclude(id=request.user.id)[:10]
        projects = request.user.projects.filter(name__icontains=query)[:10]
        rooms = request.user.rooms.filter(
            is_dm=False, name__icontains=query
        )[:10]

    return render(
        request,
        "core/search_results.html",
        {
            "query": query,
            "people": people,
            "projects": projects,
            "rooms": rooms,
        },
    )


@login_required
def notifications_view(request):
    """List notifications, then mark them all as read."""

    # Grab the list first so the template can still highlight unread ones.
    items = list(request.user.notifications.all()[:50])

    # Visiting the page counts as reading everything.
    request.user.notifications.filter(read=False).update(read=True)

    return render(request, "core/notifications.html", {"items": items})
