from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Project, Task

User = get_user_model()


class ProjectTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user("alice", password="pass12345")
        self.outsider = User.objects.create_user(
            "outsider", password="pass12345"
        )
        self.client.login(username="alice", password="pass12345")

    def test_create_project_adds_creator_as_member(self):
        self.client.post(
            "/projects/new/",
            {"name": "Website Redesign", "status": "in_progress"},
        )
        project = Project.objects.get(name="Website Redesign")
        self.assertIn(self.alice, project.members.all())

    def test_non_member_cannot_open_project(self):
        project = Project.objects.create(
            name="Secret", created_by=self.alice
        )
        project.members.add(self.alice)
        self.client.login(username="outsider", password="pass12345")
        response = self.client.get(f"/projects/{project.id}/")
        self.assertEqual(response.status_code, 404)

    def test_add_task_and_toggle(self):
        project = Project.objects.create(name="P", created_by=self.alice)
        project.members.add(self.alice)

        self.client.post(
            f"/projects/{project.id}/tasks/add/",
            {"title": "Write the report", "assignee": self.alice.id},
        )
        task = Task.objects.get(title="Write the report")
        self.assertEqual(task.assignee, self.alice)
        self.assertFalse(task.done)

        self.client.post(f"/projects/tasks/{task.id}/toggle/")
        task.refresh_from_db()
        self.assertTrue(task.done)

    def test_progress_percentage(self):
        project = Project.objects.create(name="P", created_by=self.alice)
        project.members.add(self.alice)
        Task.objects.create(project=project, title="a", done=True)
        Task.objects.create(project=project, title="b", done=False)
        self.assertEqual(project.progress, 50)
