from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.core.models import notify

from .models import Message, Room

User = get_user_model()


def message_dict(message, user):
    """The JSON shape the chat panel's JavaScript expects."""
    when = timezone.localtime(message.created_at)
    return {
        "id": message.id,
        "sender": str(message.sender),
        "mine": message.sender_id == user.id,
        "text": message.text,
        "time": when.strftime("%I:%M %p").lstrip("0"),
    }


@login_required
def room_list(request):

    # The user's team rooms (DMs live in the sidebar instead).
    rooms = request.user.rooms.filter(is_dm=False).prefetch_related(
        "members"
    )

    return render(request, "chat/room_list.html", {"rooms": rooms})


@login_required
def room_create(request):

    friends = request.user.friends()
    projects = request.user.projects.all()

    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        if not name:
            return render(
                request,
                "chat/room_form.html",
                {
                    "friends": friends,
                    "projects": projects,
                    "error": "The room needs a name.",
                },
            )

        # Optional link to one of the user's projects.
        project = None
        project_id = request.POST.get("project")
        if project_id:
            project = projects.filter(id=project_id).first()

        room = Room.objects.create(
            name=name,
            description=request.POST.get("description", "").strip(),
            project=project,
            created_by=request.user,
        )

        # The creator is always a member.
        room.members.add(request.user)

        # Add the chosen friends and let them know.
        for friend in friends.filter(id__in=request.POST.getlist("members")):
            room.members.add(friend)
            notify(
                friend,
                f'{request.user} added you to #{room.name}.',
                f"/chat/{room.id}/",
            )

        return redirect(f"/chat/{room.id}/")

    return render(
        request,
        "chat/room_form.html",
        {"friends": friends, "projects": projects},
    )


@login_required
def room_detail(request, room_id):

    # Only members can open a room.
    room = get_object_or_404(Room, id=room_id, members=request.user)

    # Last 50 messages, oldest first for display.
    chat_messages = list(
        room.messages.select_related("sender").order_by("-created_at")[:50]
    )[::-1]

    return render(
        request,
        "chat/room_detail.html",
        {
            "room": room,
            "room_title": room.display_name(request.user),
            "chat_messages": chat_messages,
            "members": room.members.all(),
            # One click starts a video call for everyone in the room.
            "video_url": f"https://meet.jit.si/TeamSpace-room-{room.id}",
        },
    )


@login_required
@require_POST
def send_message(request, room_id):

    # Only members can post.
    room = get_object_or_404(Room, id=room_id, members=request.user)

    text = request.POST.get("text", "").strip()
    if text:
        message = Message.objects.create(
            room=room, sender=request.user, text=text
        )
    else:
        message = None

    # The chat panel posts with fetch() and wants JSON back.
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        if message is None:
            return JsonResponse({"ok": False}, status=400)
        return JsonResponse(
            {"ok": True, "message": message_dict(message, request.user)}
        )

    # Plain form submit (no JavaScript) just returns to the room.
    return redirect(f"/chat/{room.id}/")


@login_required
def messages_json(request, room_id):

    # Only members can read.
    room = get_object_or_404(Room, id=room_id, members=request.user)

    # Only messages newer than the last one the client has.
    after = request.GET.get("after", "0")
    after_id = int(after) if after.isdigit() else 0

    new_messages = room.messages.select_related("sender").filter(
        id__gt=after_id
    )[:100]

    return JsonResponse(
        {
            "messages": [
                message_dict(m, request.user) for m in new_messages
            ]
        }
    )


@login_required
def start_dm(request, user_id):

    other = get_object_or_404(User, id=user_id)

    # You can only message your friends.
    if not request.user.is_friends_with(other):
        return redirect("/people/")

    # Reuse the existing conversation if there is one.
    room = (
        Room.objects.filter(is_dm=True, members=request.user)
        .filter(members=other)
        .first()
    )
    if room is None:
        room = Room.objects.create(is_dm=True, created_by=request.user)
        room.members.add(request.user, other)

    return redirect(f"/chat/{room.id}/")
