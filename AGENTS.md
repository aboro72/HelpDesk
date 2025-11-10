# Repository Guidelines

## Project Structure & Module Organization
- `helpdesk/`: Django project config (`settings.py`, `urls.py`, `wsgi.py`).
- `apps/`: Feature apps (e.g., `accounts`, `tickets`, `knowledge`, `chat`, `admin_panel`, `main`).
- `templates/`: Project-level templates (added to `TEMPLATES['DIRS']`).
- `static/`: CSS/JS/images (CKEditor and theme assets included).
- `websites/`: Static marketing/demo pages.
- Root tests: `test_*.py` files live at repo root (pytest).
- Utilities: `tools/`, SSL dev certs in `ssl/`, helper scripts like `run_http.bat`, `run_https.bat`, `start_server.bat`.

## Build, Test, and Development Commands
- Create env: `python -m venv .venv && .venv\\Scripts\\activate`
- Install deps: `pip install -r requirements.txt`
- Migrate DB: `python manage.py migrate`
- Run dev server (HTTP): `python manage.py runserver`
- Run dev server (HTTPS): `run_https.bat` (uses `ssl/localhost.crt|.key`)
- Run tests: `pytest -q` (use `-k <expr>` to filter; coverage via `pytest --cov`)

## Coding Style & Naming Conventions
- Python 3, PEP 8, 4-space indentation.
- Names: `snake_case` for modules/functions/variables; `PascalCase` for classes; Django apps under `apps/<app_name>`.
- Type hints encouraged for new/modified code. Add short docstrings for public functions and views.
- Django: keep app-specific templates/static inside each app when possible; shared assets in project `templates/` and `static/`.

## Testing Guidelines
- Framework: `pytest`, `pytest-django` configured via `requirements.txt`.
- Location: Root-level `test_*.py`; per-app tests may be placed under the app as it grows.
- Naming: `test_<unit>.py` with function tests `test_<behavior>()`.
- Coverage: aim for ≥80% on touched modules; include tests for views, models, and Celery tasks (e.g., `apps/tickets/tasks.py`).

## Commit & Pull Request Guidelines
- History shows mixed brevity (e.g., "neu") and English/German. Standardize to imperative topic lines (max ~72 chars).
  - Examples: `feat(tickets): add reply-from email flow`, `fix(chat): handle CORS for iframe`.
- PRs: include summary, linked issue, test notes, and screenshots for UI changes; list env or migration impacts.

## Security & Configuration Tips
- Configure via `.env` (e.g., `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `DATABASE_URL`, `HTTPS_ENABLED`, `SITE_URL`).
- Local default DB is SQLite; MySQL/Postgres supported via `DATABASE_URL`.
- Do not commit secrets or real certs; use `ssl/` only for local dev.

