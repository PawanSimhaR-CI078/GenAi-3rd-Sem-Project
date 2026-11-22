# TOLSTOY

AI Story to Comic Script Generator.

TOLSTOY converts a user's story idea or story content into a structured written comic script using Google's Gemini API. It produces text only — no images.

## Key Features (Planned)

- User registration and login
- Story creation, editing, and lifecycle management (Editing / Completed)
- Comic script generation via Gemini (structured JSON)
- Application token system with periodic refill
- Administrator analytics dashboard (~5–6 charts)
- User/story management for administrators
- Database viewer (no secrets exposed)
- Maintenance mode
- Email contact to administrators

## Technology Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 (target) |
| Backend | Flask |
| Database | SQLite (`database/tolstoy.db`) |
| Templates | Jinja2 |
| Styling | CSS3 (+ optional Tailwind via CDN) |
| Frontend scripting | Vanilla JavaScript |
| Charts | Chart.js (CDN) |
| AI | Google Gemini API |
| Auth | Flask sessions |
| Testing | pytest + Postman |

No Node.js, npm, or frontend build step is required.

## Folder Structure

```
TOLSTOY/
├── agents.md
├── context.md
├── readme.md
├── run.py
├── requirements.txt
├── .env.example
├── .gitignore
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── extensions.py
│   ├── models/
│   ├── routes/ (api/, pages/)
│   ├── services/
│   ├── security/
│   ├── schemas/
│   ├── templates/ (public/, user/, admin/, errors/)
│   └── static/ (css/, js/, images/)
├── database/ (migrations/, backups/, exports/)
├── markdown/ (7 documents)
├── postman/
├── scripts/
└── tests/
```

## Prerequisites

- Python 3.12 (target; 3.14 currently installed — recreate `.venv` if the pin is required)
- Git
- No Node.js/npm required

## Environment Setup

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

Create `.env` from the template:

```powershell
Copy-Item .env.example .env
```

Fill in values in `.env` (never commit `.env`). See `.env.example` for all variable names.

## Dependency Installation

Dependencies are not yet pinned. The intended categories are listed in `requirements.txt` (currently only a placeholder). Final versions will be selected during implementation. Do not install the full stack yet.

## Running the Application

Not yet runnable — application code is not implemented. Once implemented, the entry point will be `run.py`:

```powershell
python run.py
```

(Planned; not currently available.)

## Database

- Location: `database/tolstoy.db` (not created yet)
- Exactly three tables: `tolstoy_users`, `tolstoy_stories`, `tolstoy_system_settings`
- Migrations: `database/migrations/`
- Backups: `database/backups/`
- Exports: `database/exports/`

## Testing

- Automated: pytest (not yet implemented)
- API: Postman collection (not yet created)

## Documentation

Read in this order:

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

## Current Status

Initial project setup and complete documentation authoring phase. No application code, database schema, APIs, or frontend pages have been implemented. All Markdown files are populated as the technical blueprint.

## Git

- Branch: `main`
- Remote: `https://github.com/PawanSimha/TOLSTOY-Comic-to-Story-Script-Generator.git`
- Push pending owner credential access (see setup notes).