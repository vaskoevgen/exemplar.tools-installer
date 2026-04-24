# Task

Build a Todo List web application with a Python/FastAPI backend, PostgreSQL database, and a single-page vanilla JavaScript frontend.

## Requirements

### Backend (FastAPI, Python)

- `POST /tasks` — create a task with `{"title": "string"}` body; return the created task object
- `GET /tasks` — list all tasks; accept optional `?completed=true` or `?completed=false` query param
- `PATCH /tasks/{id}` — update a task; accept `{"completed": true/false}` body; return updated task
- `DELETE /tasks/{id}` — delete a task; return 204 No Content
- Serve the `static/index.html` file at `GET /`
- Use PostgreSQL via DATABASE_URL environment variable (psycopg2)
- Error responses: JSON with `{"detail": "message"}`, appropriate HTTP status codes (404 for missing task)

### Database

PostgreSQL table `tasks`:
- `id` SERIAL PRIMARY KEY
- `title` VARCHAR(500) NOT NULL
- `completed` BOOLEAN NOT NULL DEFAULT FALSE
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT NOW()

### Frontend (static/index.html)

Single HTML file with inline CSS and JavaScript (no external dependencies, no build step):
- Show all tasks in a list
- Input + button to add a new task
- Checkbox to toggle task completion
- Button to delete a task
- Filter buttons: All / Active / Completed
- Auto-refresh after each operation (re-fetch from API)

### README.md

Include instructions for:
- Starting the PostgreSQL database with Docker
- Installing Python dependencies
- Running the backend server
- Opening the app in a browser
- Full API endpoint reference

## Storage

DATABASE_URL environment variable points to the PostgreSQL connection string.

## Constraints

- Python 3.11+
- FastAPI + uvicorn for the web server
- psycopg2-binary for PostgreSQL
- No ORM — use raw SQL queries
- Single Python source file for the backend: `src/root/main.py`
- Frontend: single file `src/root/static/index.html`
- No authentication
- No pagination
