# CSCI-3340-Final-Project

Project-centred group communication. Chat organised around projects rather than
around teams, with generated summaries of decisions, a project timeline, and a
completion estimate derived from what is being discussed.

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

The first person to set up must generate the initial migration, because the
custom user model has no migration file yet:

```bash
python manage.py makemigrations accounts
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Commit and push the generated apps/accounts/migrations/0001_initial.py.
Everyone after that only runs migrate.

Open http://127.0.0.1:8000/ — you should see "Project is running."

## Running tests

```bash
python manage.py test
```

## Layout

```
config/           settings, root URLs, WSGI/ASGI entrypoints
apps/accounts/    custom user model
apps/core/        shared views, base templates
apps/projects/    projects, membership, roles
apps/chat/        rooms and messages
apps/schedule/    calendar events and milestones
apps/insights/    generated summaries, decisions, estimates
static/           CSS, JS, images
templates/        project-level templates
```

The placeholder apps are empty on purpose. Add models.py, views.py, and
urls.py to each as work begins, and register each new urls.py in
config/urls.py.

Apps have no apps.py; Django infers the config from the INSTALLED_APPS
entry. Add one only if an app needs startup hooks such as signal registration.

## Rules

- Never commit .env or db.sqlite3.
- Always commit migration files — teammates need them to build the database.
- Re-run pip freeze > requirements.txt after installing a new package.
- Do not change AUTH_USER_MODEL.
