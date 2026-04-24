# Todo List Web Application

## What to build

A web application for managing personal tasks. Users can create tasks, mark them complete, and delete them.

## Technology stack

- **Backend**: Python + FastAPI, exposing a REST JSON API
- **Database**: PostgreSQL — one table: `tasks`
- **Frontend**: Single HTML page with vanilla JavaScript (no build step, served by the backend as static file)

## Features

1. **Create task** — POST /tasks — JSON body with a title field — returns the created task
2. **List tasks** — GET /tasks — returns all tasks (with optional ?completed=true/false filter)
3. **Complete task** — PATCH /tasks/{id} — JSON body with completed field set to true — marks a task done
4. **Delete task** — DELETE /tasks/{id} — removes a task permanently

## Database schema

Table: `tasks`
- `id` — SERIAL PRIMARY KEY
- `title` — VARCHAR(500) NOT NULL
- `completed` — BOOLEAN NOT NULL DEFAULT FALSE
- `created_at` — TIMESTAMPTZ NOT NULL DEFAULT NOW()

## API responses

All endpoints return JSON. Errors return a JSON object with a "detail" key describing the error.

## Non-requirements

- No authentication or user accounts
- No pagination (return all tasks)
- No categories or priorities
- No undo functionality

## Deployment

Single Python process. Database connection via DATABASE_URL environment variable.

## README requirement

Include a `README.md` with:
- How to start the database
- How to run the backend
- API endpoint reference
- How to open the frontend
