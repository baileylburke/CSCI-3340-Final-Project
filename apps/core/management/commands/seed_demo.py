"""Fills the database with demo data so the app has something to show.

Usage:
    python manage.py seed_demo

Safe to run more than once, since it looks up existing rows before
creating. All demo users share the password printed at the end.
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import FriendRequest
from apps.chat.models import Message, Room
from apps.core.models import Notification
from apps.projects.models import Project, Task
from apps.schedule.models import Event

User = get_user_model()

PASSWORD = "demo1234"


class Command(BaseCommand):
    help = "Create demo users, projects, rooms, tasks, and events."

    def handle(self, *args, **options):
        now = timezone.now()
        today = timezone.localdate()

        # ----- Users ---------------------------------------------------
        people = {
            "jason": "Jason Lopez",
            "bailey": "Bailey Burke",
            "alfred": "Alfred Zavala",
            "emma": "Emma Johnson",
            "michael": "Michael Chen",
        }
        users = {}
        for username, display_name in people.items():
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "display_name": display_name,
                    "email": f"{username}@example.com",
                },
            )
            if created:
                user.set_password(PASSWORD)
                user.save()
            users[username] = user

        # Presence: who looks online / away / offline right now.
        User.objects.filter(pk=users["alfred"].pk).update(last_seen=now)
        User.objects.filter(pk=users["michael"].pk).update(last_seen=now)
        User.objects.filter(pk=users["bailey"].pk).update(
            last_seen=now - timedelta(minutes=12)
        )

        # ----- Friendships ---------------------------------------------
        pairs = [
            ("jason", "bailey"),
            ("jason", "alfred"),
            ("jason", "emma"),
            ("jason", "michael"),
            ("bailey", "alfred"),
        ]
        for a, b in pairs:
            FriendRequest.objects.get_or_create(
                from_user=users[a],
                to_user=users[b],
                defaults={"accepted": True},
            )

        # ----- Projects and tasks --------------------------------------
        def project(name, status, due_days, members, tasks):
            proj, created = Project.objects.get_or_create(
                name=name,
                defaults={
                    "status": status,
                    "due_date": today + timedelta(days=due_days),
                    "created_by": users["jason"],
                    "description": f"Demo project: {name}.",
                },
            )
            if created:
                proj.members.add(*[users[m] for m in members])
                for title, assignee, due_days_t, done in tasks:
                    Task.objects.create(
                        project=proj,
                        title=title,
                        assignee=users[assignee] if assignee else None,
                        due_date=today + timedelta(days=due_days_t),
                        done=done,
                    )
            return proj

        website = project(
            "Website Redesign", "in_progress", 12,
            ["jason", "bailey", "alfred"],
            [
                ("Create wireframes", "jason", 1, True),
                ("Build landing page", "bailey", 3, True),
                ("Set up the style guide", "alfred", 4, True),
                ("Hook up the contact form", "jason", 5, False),
                ("QA pass on mobile", "bailey", 7, False),
            ],
        )
        project(
            "Mobile App", "in_progress", 15,
            ["jason", "alfred", "michael"],
            [
                ("Sketch onboarding flow", "alfred", 2, True),
                ("Login screen", "michael", 4, True),
                ("Push notifications", "jason", 6, False),
                ("App store screenshots", None, 9, False),
                ("Beta test round 1", "michael", 10, False),
            ],
        )
        project(
            "Marketing Campaign", "planning", 23,
            ["jason", "emma"],
            [
                ("Draft campaign brief", "emma", 3, True),
                ("Collect brand assets", "jason", 6, False),
                ("Schedule social posts", "emma", 8, False),
                ("Book ad slots", None, 12, False),
                ("Review analytics plan", "jason", 14, False),
            ],
        )
        alpha = project(
            "Product Launch", "in_progress", 33,
            ["jason", "bailey", "alfred", "emma", "michael"],
            [
                ("Freeze feature list", "jason", 1, True),
                ("Write release notes", "bailey", 2, True),
                ("Prepare demo script", "alfred", 3, True),
                ("Press kit", "emma", 5, False),
                ("Launch day checklist", "michael", 6, True),
            ],
        )

        # ----- Rooms and messages --------------------------------------
        def room(name, description, members, project_obj=None, messages=()):
            r, created = Room.objects.get_or_create(
                name=name,
                is_dm=False,
                defaults={
                    "description": description,
                    "created_by": users["jason"],
                    "project": project_obj,
                },
            )
            if created:
                r.members.add(*[users[m] for m in members])
                for sender, text in messages:
                    Message.objects.create(
                        room=r, sender=users[sender], text=text
                    )
            return r

        room(
            "Design Team", "UI/UX design and feedback",
            ["jason", "bailey", "alfred"], website,
            [
                ("alfred", "New mockups are in the shared folder."),
                ("bailey", "Love the new color palette!"),
            ],
        )
        room(
            "Development Team", "Frontend, Backend, DevOps",
            ["jason", "bailey", "alfred", "michael"], website,
            [
                ("alfred", "Hey team! Just pushed the latest updates to the repo."),
                ("bailey", "Great! I'll review the changes and test on staging."),
                ("jason", "Don't forget our deadline is next Friday. Let's stay on track!"),
                ("michael", "I'll set up a quick call to discuss the API integration."),
            ],
        )
        room(
            "Marketing Team", "Campaigns and content",
            ["jason", "emma"], None,
            [("emma", "First draft of the campaign brief is ready for review.")],
        )
        room(
            "Project Alpha", "Planning and execution",
            ["jason", "bailey", "alfred", "emma"], alpha,
            [("jason", "Kickoff notes are pinned. Read before Friday please!")],
        )
        room(
            "Random", "General discussions",
            ["jason", "bailey", "alfred", "emma", "michael"], None,
            [("michael", "Lunch at the usual place today?")],
        )

        # A direct message thread so the sidebar has something in it.
        dm = (
            Room.objects.filter(is_dm=True, members=users["jason"])
            .filter(members=users["alfred"])
            .first()
        )
        if dm is None:
            dm = Room.objects.create(is_dm=True, created_by=users["jason"])
            dm.members.add(users["jason"], users["alfred"])
            Message.objects.create(
                room=dm,
                sender=users["alfred"],
                text="Can you review the calendar widget when you get a sec?",
            )

        # ----- Events ---------------------------------------------------
        events = [
            ("Team Standup", alpha, today, "09:30"),
            ("Sprint Demo", website, today, "15:00"),
            ("Project Alpha Deadline", alpha, today + timedelta(days=2), "23:59"),
            ("Design Review Meeting", website, today + timedelta(days=3), "10:00"),
        ]
        for title, proj, date, hhmm in events:
            hour, minute = (int(x) for x in hhmm.split(":"))
            starts_at = timezone.make_aware(
                timezone.datetime(date.year, date.month, date.day, hour, minute)
            )
            Event.objects.get_or_create(
                title=title,
                defaults={
                    "project": proj,
                    "created_by": users["jason"],
                    "starts_at": starts_at,
                },
            )

        # ----- Notifications --------------------------------------------
        if not Notification.objects.filter(user=users["jason"]).exists():
            Notification.objects.create(
                user=users["jason"],
                text='New project assigned: "Website Redesign".',
                link="/projects/",
            )
            Notification.objects.create(
                user=users["jason"],
                text='Task due soon: "Hook up the contact form".',
                link="/projects/tasks/",
            )
            Notification.objects.create(
                user=users["jason"],
                text="Emma Johnson posted in #Marketing Team.",
                link="/chat/",
            )

        self.stdout.write(self.style.SUCCESS("Demo data ready."))
        self.stdout.write(
            f"Log in as any of: {', '.join(people)} (password: {PASSWORD})"
        )
