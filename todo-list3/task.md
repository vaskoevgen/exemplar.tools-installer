# Task

Build a task management web application with a decoupled three-tier architecture: a React frontend, a FastAPI backend, and a PostgreSQL database. The three components must remain separate and communicate only via HTTP REST API.

## Component 1 — Database (PostgreSQL, port 5432)

The tasks table already exists with this schema:
- id SERIAL PRIMARY KEY
- title VARCHAR(255) NOT NULL
- description TEXT
- status VARCHAR(20) NOT NULL DEFAULT 'pending'
- created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
- updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()

## Component 2 — Backend (FastAPI, Python, port 8000)

A FastAPI application that connects to PostgreSQL via DATABASE_URL environment variable using psycopg2.

Six endpoints:
- GET /health — returns a JSON object with a status field set to ok
- GET /tasks — list all tasks, returns a JSON array of task objects
- POST /tasks — create a task, body has title (required string), description (optional string), status (optional string defaulting to pending)
- GET /tasks/{id} — get a single task by integer id, returns 404 with detail field if not found
- PUT /tasks/{id} — update a task by id, body has optional title, description, and status fields, returns 404 if not found
- DELETE /tasks/{id} — delete a task by id, returns 404 if not found

Rules:
- Task status must be one of: pending, in_progress, done
- Status transitions are free-form (any direction allowed)
- created_at is set on creation and never changes
- updated_at is set automatically by the backend on every update
- Hard delete — remove the row completely on DELETE
- All endpoints return JSON
- On 404 return a JSON object with a detail field

A task object has: id (integer), title (string), description (string or null), status (string), created_at (ISO timestamp string), updated_at (ISO timestamp string)

## Component 3 — Frontend (React + Vite, TypeScript, port 5173)

A React single-page application that calls the backend REST API via VITE_API_URL environment variable (defaults to http://localhost:8000).

The UI must have:
- A list of all tasks showing title, status badge, and created date
- Status badge colors: pending in grey, in_progress in blue, done in green
- A form to create a new task with title, description, and status fields
- An edit button per task to update title, description, and status inline
- A delete button per task
- No page reloads — all operations update the UI without refreshing

## Architecture constraints

- Frontend communicates with backend only via HTTP REST API
- Backend is the only component that writes to the database
- No shared code between frontend and backend
- Each component must be startable independently
