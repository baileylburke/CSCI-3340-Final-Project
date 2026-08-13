from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.core.urls")),
    path("", include("apps.accounts.urls")),
    path("projects/", include("apps.projects.urls")),
    path("chat/", include("apps.chat.urls")),
    path("calendar/", include("apps.schedule.urls")),
]
