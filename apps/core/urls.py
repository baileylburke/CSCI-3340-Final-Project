from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    # Landing page for visitors, dashboard for logged-in users.
    path("", views.index, name="index"),

    # Topbar search results.
    path("search/", views.search, name="search"),

    # Notifications list.
    path("notifications/", views.notifications_view, name="notifications"),
]
