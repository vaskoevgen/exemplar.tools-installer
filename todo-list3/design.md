# Design: todo-list3

*Version 1 — Auto-maintained by pact*

## Decomposition

- [C] **Root** (`root`)
  # Task

Build a task management web application with a decoupled three-tier architecture: a React frontend, a FastAPI backend, and a PostgreSQL database. The three components must remain separate and 
  - [C] **FastAPI Backend API** (`backend`)
    A FastAPI application running on port 8000 that implements the task management REST API. Connects to PostgreSQL via DATABASE_URL env var using psycopg2.pool for connection pooling (A8). Uses synchronous def endpoints with FastAPI's thread-pool executor (A9). CORS middleware configured to allow frontend origin (A5, AC21).

Endpoints:
- GET /health → {"status": "ok"} (AC3)
- GET /tasks → JSON array of all tasks ordered by created_at DESC (A3, AC7)
- POST /tasks → 201 + full task object; title required, description optional (null if omitted/empty per A12), status optional defaulting to 'pending'; status validated against {pending, in_progress, done} returning 422 on invalid (A6, AC4-AC6)
- GET /tasks/{id} → task object or 404 with detail (AC8-AC9)
- PUT /tasks/{id} → PATCH semantics: only provided fields are updated, created_at never modified, updated_at set to NOW(); status validated; 404 if not found (A1, AC10-AC11)
- DELETE /tasks/{id} → hard delete, 200 with JSON confirmation, 404 if not found (AC12-AC13)

All timestamps serialized as ISO 8601 with timezone (AC14). All public functions type-annotated (AC22). Files kept under 300 lines (AC25).

Structure: main.py (app, CORS, lifespan/pool init), models.py (Pydantic schemas), db.py (pool management, query helpers), routes.py (endpoint handlers).

Includes a full pytest test suite: unit tests for validation/serialization logic and contract tests against a live PostgreSQL instance (via DATABASE_URL) exercising all six endpoints (AC23-AC24). Test setup/teardown manages its own test data (A10).
  - [C] **PostgreSQL Database Schema** (`database`)
    PostgreSQL database initialization on port 5432. Provides an SQL init script that creates the `tasks` table with columns: id SERIAL PRIMARY KEY, title VARCHAR(255) NOT NULL, description TEXT, status VARCHAR(20) NOT NULL DEFAULT 'pending', created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(). This is a standalone schema definition — no application logic. The init script should be idempotent (CREATE TABLE IF NOT EXISTS). Satisfies AC1.
  - [ ] **React Frontend SPA** (`frontend`)
    A React + Vite + TypeScript single-page application running on port 5173 that provides the task management UI. Communicates with the backend exclusively via HTTP REST API using VITE_API_URL env var (defaulting to http://localhost:8000) (AC20).

UI features:
- Task list displaying title, colored status badge (grey=pending, blue=in_progress, green=done), and formatted created date (AC15-AC16)
- Create task form with title (required), description (optional, sends null for empty per A12), and status dropdown (AC17)
- Inline edit-in-place per task row: toggling between display mode and form mode to modify title, description, status; persists via PUT to backend (A7, AC18)
- Delete button per task row with immediate UI removal on success (AC19)
- All operations are SPA-style — no page reloads; state managed via useState/useEffect (A11)

Structure: App.tsx (root, state, effects), components/TaskList.tsx, components/TaskItem.tsx (display + inline edit toggle), components/TaskForm.tsx (create form), api.ts (typed fetch wrappers for all endpoints), types.ts (Task interface). Files kept under 300 lines (AC25). No shared code with backend (AC26).
