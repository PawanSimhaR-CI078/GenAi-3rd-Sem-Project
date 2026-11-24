# TOLSTOY

AI Story to Comic Script Generator. TOLSTOY turns a story idea into a structured **written** comic script (scenes, panels, dialogue, narration) using Google's Gemini API. No images are generated.

## Key Features

- User registration, login, logout and session-cookie auth
- Story creation, editing, lifecycle (`EDITING` / `COMPLETED`) and generation state
- Comic script generation through a single Gemini service
- Application tokens: 5 on signup, +5 every 48 hours, server-side cost, refund on failure
- Admin analytics board with KPIs, 9 charts, database health and integrity checks
- Admin user editing, role access, read-only live database, settings and system offline control
- Maintenance mode that blocks users but keeps the admin area reachable
- CSRF protection, hashed passwords, parameterized SQL and Jinja autoescaping

## Technology Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 target (3.14 works in the current venv) |
| Backend | Flask application factory + blueprints |
| Database | SQLite at `database/tolstoy.db`, exactly three tables |
| Templates | Jinja2 |
| Styling | Hand-written CSS3 (+ Tailwind and Chart.js via CDN) |
| Frontend | Vanilla JavaScript, no build step |
| AI | Google Gemini API |
| Testing | pytest + Postman/SIT script |

No Node.js, npm or frontend build step is required.

## Quick start

```powershell
# 1. Create and activate a virtual environment
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install pinned dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 3. Create your local environment file (never commit it)
Copy-Item .env.example .env

# 4. Create the database, seed demo data, then run
python scripts/seed_data.py
python run.py
```

Open `http://127.0.0.1:5001`.

> Only Python 3.14 is installed on this machine; the 3.12 target is a project pin, not a blocker for local development.

## Environment variables

`.env.example` is the authoritative template. `.env` is gitignored.

| Variable | Purpose |
|---|---|
| `FLASK_APP`, `FLASK_ENV` | Entry point and config (`development`, `production`, `testing`) |
| `SECRET_KEY` | Flask session signing key — generate a random value before production |
| `DATABASE_PATH` | SQLite path, default `database/tolstoy.db` |
| `GEMINI_API_KEY`, `GEMINI_MODEL` | Generation credentials — key lives only in `.env` |
| `MAIL_*`, `ADMIN_EMAIL` | Contact-form delivery; leave blank to disable |
| `SUPER_ADMIN_USERNAME` / `SUPER_ADMIN_PASSWORD` | Bootstrap super admin |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | Bootstrap admin #1 |
| `ADMIN2_USERNAME` / `ADMIN2_PASSWORD` | Bootstrap admin #2 |

Bootstrap creates these accounts only when the username does not already exist, so restarting never resets passwords or permissions.

## Demo accounts (after `seed_data.py`)

| Role | Username | Password |
|---|---|---|
| SUPER_ADMIN | `Pawan Simha R` | `iamsuperadmin` |
| ADMIN | `Ramesh` | `iamadmin` |
| ADMIN | `Suresh` | `iamadmin` |
| USER | 55 generated users | `iamuser` |

These are local demo credentials. Change them before any real deployment.

## Roles and what each can do

| Area | USER | ADMIN | SUPER_ADMIN |
|---|:--:|:--:|:--:|
| Dashboard, stories, wallet, profile | ✓ | – | – |
| Analytics dashboard | – | ✓ | ✓ |
| View / edit user details | – | ✓ | ✓ |
| Live database (read-only) | – | ✓ | ✓ |
| Stories administration | – | ✓ | ✓ |
| Role Access (RBAC matrix + role assignment) | – | – | ✓ |
| Token wallet increases | – | – | ✓ |
| System settings | – | – | ✓ |
| Take system offline | – | – | ✓ |

Capabilities live as JSON in `tolstoy_system_settings` (`role_permissions`). Five capabilities are permanently SUPER_ADMIN-only and cannot be granted through the matrix.

## Database

- Location: `database/tolstoy.db` (gitignored)
- Exactly three tables: `tolstoy_users`, `tolstoy_stories`, `tolstoy_system_settings`
- Schema: `database/migrations/001_initial_schema.sql`
- Rebuild demo data: `python scripts/seed_data.py` (deletes all existing rows)

## Verification

```powershell
.\.venv\Scripts\python.exe -m pytest -q        # 19 tests
.\.venv\Scripts\python.exe scripts\sit_check.py  # live SIT against 127.0.0.1:5001
```

## Documentation

1. `agents.md`
2. `context.md`
3. `readme.md`
4. `markdown/plan.md`
5. `markdown/architecture.md`
6. `markdown/database.markdown`
7. `markdown/api.md`
8. `markdown/ui_ux.md`
9. `markdown/security.md`
10. `markdown/testing.md`

## Git

- Branch: `main`
- Remote: `https://github.com/PawanSimhaR-CI078/GenAi-3rd-Sem-Project.git`
