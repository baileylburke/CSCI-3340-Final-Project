from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.core.models import notify

from .models import Project, Task


@login_required
def project_list(request):

    # Only projects the user is a member of.
    projects = request.user.projects.all()

    return render(
        request,
        "projects/project_list.html",
        {"projects": projects},
    )


@login_required
def project_create(request):

    friends = request.user.friends()

    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        if not name:
            return render(
                request,
                "projects/project_form.html",
                {"friends": friends, "error": "The project needs a name."},
            )

        project = Project.objects.create(
            name=name,
            description=request.POST.get("description", "").strip(),
            due_date=request.POST.get("due_date") or None,
            status=request.POST.get("status", "planning"),
            created_by=request.user,
        )

        # The creator is always a member.
        project.members.add(request.user)

        # Add the chosen friends and let them know.
        for friend in friends.filter(id__in=request.POST.getlist("members")):
            project.members.add(friend)
            notify(
                friend,
                f'{request.user} added you to the project "{project.name}".',
                f"/projects/{project.id}/",
            )

        return redirect(f"/projects/{project.id}/")

    return render(
        request,
        "projects/project_form.html",
        {"friends": friends},
    )


@login_required
def project_detail(request, project_id):

    # Only members can open a project.
    project = get_object_or_404(
        Project, id=project_id, members=request.user
    )

    return render(
        request,
        "projects/project_detail.html",
        {
            "project": project,
            "tasks": project.tasks.select_related("assignee"),
            "members": project.members.all(),
            "events": project.events.all(),
        },
    )


@login_required
@require_POST
def add_task(request, project_id):

    # Only members can add tasks.
    project = get_object_or_404(
        Project, id=project_id, members=request.user
    )

    title = request.POST.get("title", "").strip()
    if not title:
        return redirect(f"/projects/{project.id}/")

    # The assignee must be a member of the project.
    assignee = None
    assignee_id = request.POST.get("assignee")
    if assignee_id:
        assignee = project.members.filter(id=assignee_id).first()

    task = Task.objects.create(
        project=project,
        title=title,
        assignee=assignee,
        due_date=request.POST.get("due_date") or None,
    )

    # Tell the assignee, unless they assigned it to themselves.
    if assignee and assignee != request.user:
        notify(
            assignee,
            f'{request.user} assigned you "{task.title}" '
            f'in {project.name}.',
            f"/projects/{project.id}/",
        )

    return redirect(f"/projects/{project.id}/")


@login_required
@require_POST
def toggle_task(request, task_id):

    # Any member of the task's project can tick it off.
    task = get_object_or_404(
        Task, id=task_id, project__members=request.user
    )

    task.done = not task.done
    task.save()

    # Go back to wherever the form said to (a path on this site only).
    next_url = request.POST.get("next", "")
    if not next_url.startswith("/") or next_url.startswith("//"):
        next_url = f"/projects/{task.project_id}/"
    return redirect(next_url)


@login_required
def my_tasks(request):

    # Everything assigned to the current user.
    tasks = request.user.tasks.select_related("project")

    return render(request, "projects/my_tasks.html", {"tasks": tasks})
