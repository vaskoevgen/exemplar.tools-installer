# Task

Build a personal task management web app with a React frontend, Express/Node.js backend, and PostgreSQL database.

## Requirements

### Backend (Express/Node.js)

- REST API with the following endpoints:
  - `POST /tasks` — create a task (title required, returns 400 if title is empty/missing)
  - `GET /tasks` — list all tasks
  - `GET /tasks/:id` — get a single task (returns 404 if not found)
  - `PATCH /tasks/:id` — update title, completed, priority, or due_date (returns 404 if not found)
  - `DELETE /tasks/:id` — delete a task (returns 404 if not found)
- Task fields: `id` (uuid), `title` (varchar, NOT NULL), `completed` (boolean, default false), `priority` (integer, default 1), `due_date` (date, nullable), `created_at` (timestamptz, NOT NULL)
- Proper HTTP status codes: 200, 201, 400, 404
- Backend is authoritative — no client-side caching of state

### Database (PostgreSQL)

- Single `tasks` table with the fields above
- Normalized schema appropriate for a single-user app (no unnecessary joins)
- Index on `priority` and `due_date` for future query patterns
- At least one schema migration (e.g. adding `priority` column after initial schema)

### Frontend (React)

- List all tasks
- Create a new task (title input)
- Mark a task as complete/incomplete (toggle)
- Delete a task
- Display priority and due date if set

## Learning Goals

- Practice REST API design with correct HTTP verbs and status codes
- Practice PostgreSQL schema design and migrations
- Practice connecting a React frontend to a REST backend