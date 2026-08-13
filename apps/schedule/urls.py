from django.urls import path

from . import views

app_name = "schedule"

urlpatterns = [
    # The month calendar.
    path("", views.calendar_view, name="calendar"),

    # Add a new event.
    path("new/", views.event_create, name="event_create"),
]
