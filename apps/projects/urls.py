from django.urls import path

from . import views

app_name = "projects"

urlpatterns = [
    # All of the user's projects.
    path("", views.project_list, name="list"),

    # Create a new project.
    path("new/", views.project_create, name="create"),

    # Tasks assigned to the current user.
    path("tasks/", views.my_tasks, name="my_tasks"),

    # Tick a task done / not done.
    path("tasks/<int:task_id>/toggle/", views.toggle_task, name="toggle_task"),

    # One project's page.
    path("<int:project_id>/", views.project_detail, name="detail"),

    # Add a task to a project.
    path("<int:project_id>/tasks/add/", views.add_task, name="add_task"),
]
