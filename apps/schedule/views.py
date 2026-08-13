from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from apps.core.models import notify

from .models import Event
from .services import build_month, events_for


@login_required
def calendar_view(request):

    # Which month to show; defaults to the current one.
    today = timezone.localdate()
    try:
        year = int(request.GET.get("year", today.year))
        month = int(request.GET.get("month", today.month))
        if not 1 <= month <= 12:
            raise ValueError
    except ValueError:
        year, month = today.year, today.month

    return render(
        request,
        "schedule/calendar.html",
        {
            "calendar": build_month(request.user, year, month),
            "month_events": events_for(request.user).filter(
                starts_at__year=year, starts_at__month=month
            ),
            "upcoming_events": events_for(request.user).filter(
                starts_at__gte=timezone.now()
            )[:8],
        },
    )


@login_required
def event_create(request):

    projects = request.user.projects.all()

    if request.method == "POST":

        title = request.POST.get("title", "").strip()
        date = request.POST.get("date", "")
        time = request.POST.get("time", "") or "09:00"

        # Title and date are required.
        try:
            starts_at = timezone.make_aware(
                datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            )
        except ValueError:
            starts_at = None
        if not title or starts_at is None:
            return render(
                request,
                "schedule/event_form.html",
                {
                    "projects": projects,
                    "error": "An event needs a title and a date.",
                },
            )

        # Optional link to one of the user's projects.
        project = None
        project_id = request.POST.get("project")
        if project_id:
            project = projects.filter(id=project_id).first()

        event = Event.objects.create(
            title=title,
            description=request.POST.get("description", "").strip(),
            project=project,
            created_by=request.user,
            starts_at=starts_at,
        )

        # Tell the other project members about the new event.
        if project:
            for member in project.members.exclude(id=request.user.id):
                notify(
                    member,
                    f'{request.user} added "{event.title}" '
                    f"to {project.name}.",
                    "/calendar/",
                )

        return redirect("/calendar/")

    return render(
        request, "schedule/event_form.html", {"projects": projects}
    )
