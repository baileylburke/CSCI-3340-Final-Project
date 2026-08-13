# CSCI-3340-Final-Project

Project-centred group communication. Chat organised around projects rather than
around teams, with generated summaries of decisions, a project timeline, and a
completion estimate derived from what is being discussed.

## Team Members
Bailey Burke | Jason Lopez | Alfred Zavala

## First-time setup

```bash
git clone https://github.com/baileylburke/CSCI-3340-Final-Project.git
cd CSCI-3340-Final-Project
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS / Linux
pip install -r requirements.txt
cp .env.example .env            # then edit .env
```

Settings load .env from the project root. Variables already set in your real
environment take precedence over the file.

Then build the database and start the server:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/ and you should see the TeamSpace landing page.

## Demo data

To fill the app with example users, projects, rooms, tasks, and events
(useful for demos and screenshots):

```bash
python manage.py seed_demo
```

Then log in as `jason`, `bailey`, `alfred`, `emma`, or `michael` with the
password `demo1234`. Safe to run more than once.

## Running tests

```bash
python manage.py test
```

## Layout

```
config/           settings, root URLs, WSGI/ASGI entrypoints
apps/accounts/    custom user model, friends and friend requests
apps/core/        dashboard, search, notifications, presence middleware
apps/projects/    projects, membership, tasks
apps/chat/        rooms, direct messages, polling chat
apps/schedule/    calendar events
apps/insights/    generated summaries, decisions, estimates (not started)
static/           shared stylesheet (static/css/app.css)
templates/        base layout, sidebar/topbar, and per-app pages
```

Pages extend `templates/base.html`, which provides the sidebar and topbar.
Chat updates by polling `/chat/<id>/messages/` every few seconds, so no
WebSockets are needed. Video calls open a Jitsi Meet room in a new tab.

Apps have no apps.py; Django infers the config from the INSTALLED_APPS
entry. Add one only if an app needs startup hooks such as signal registration.

## Rules

- Never commit .env or db.sqlite3.
- Always commit migration files. Teammates need them to build the database.
- Re-run pip freeze > requirements.txt after installing a new package.
- Do not change AUTH_USER_MODEL.
