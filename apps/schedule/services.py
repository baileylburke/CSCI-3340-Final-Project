"""Helpers for building the calendar month grid."""

import calendar

from django.db.models import Q
from django.utils import timezone

from .models import Event


def events_for(user):
    """All events the user should see: their own plus their projects'."""
    return Event.objects.filter(
        Q(created_by=user) | Q(project__members=user)
    ).distinct()


def build_month(user, year=None, month=None):
    """Build the data the calendar grid template needs for one month.

    Returns a dict with the month name, year, prev/next links, and a list
    of weeks. Each week is a list of day dicts:
        {"day": 15, "in_month": True, "is_today": False, "has_event": True}
    Weeks start on Sunday to match the design.
    """
    today = timezone.localdate()
    year = year or today.year
    month = month or today.month

    # Days in this month that have at least one visible event.
    event_days = set()
    for event in events_for(user).filter(
        starts_at__year=year, starts_at__month=month
    ):
        event_days.add(timezone.localtime(event.starts_at).day)

    weeks = []
    cal = calendar.Calendar(firstweekday=6)  # Sunday first.
    for week in cal.monthdayscalendar(year, month):
        row = []
        for day in week:
            row.append(
                {
                    "day": day,
                    "in_month": day != 0,
                    "is_today": (
                        day == today.day
                        and month == today.month
                        and year == today.year
                    ),
                    "has_event": day in event_days,
                }
            )
        weeks.append(row)

    # Previous and next month, for the arrows.
    prev_year, prev_month = (year, month - 1) if month > 1 else (year - 1, 12)
    next_year, next_month = (year, month + 1) if month < 12 else (year + 1, 1)

    return {
        "month_name": calendar.month_name[month],
        "year": year,
        "weeks": weeks,
        "prev_year": prev_year,
        "prev_month": prev_month,
        "next_year": next_year,
        "next_month": next_month,
    }
