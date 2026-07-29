# Contributing

## Branching

Do not commit directly to main.

```bash
git checkout main
git pull
git checkout -b feature/short-description
```

Prefixes: feature/, fix/, docs/

## Pull requests

1. Push the branch: git push -u origin feature/short-description
2. Open a pull request against main.
3. Request review from at least one teammate.
4. Merge after approval, then delete the branch.

## Ownership

Each app has one primary owner to limit merge conflicts:

| App        | Owner |
| ---------- | ----- |
| accounts   | TBD   |
| projects   | TBD   |
| chat       | TBD   |
| schedule   | TBD   |
| insights   | TBD   |

## Before pushing

- python manage.py test passes
- No .env, db.sqlite3, or __pycache__ in the diff
- New packages added to requirements.txt

## Migration conflicts

If two people generate migrations at the same time, do not hand-edit them:

```bash
python manage.py makemigrations --merge
```
