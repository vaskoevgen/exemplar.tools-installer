# Design: todo-list3

*Version 1 — Auto-maintained by pact*

## Decomposition

- [+] **Root** (`root`)
  # Task

Build a task management web application with a decoupled three-tier architecture: a React frontend, a FastAPI backend, and a PostgreSQL database. The three components must remain separate and 
  Tests: 0/0 passed
  - [+] **FastAPI Backend API** (`backend`)
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
    Tests: 77/77 passed
  - [+] **PostgreSQL Database Schema** (`database`)
    PostgreSQL database initialization on port 5432. Provides an SQL init script that creates the `tasks` table with columns: id SERIAL PRIMARY KEY, title VARCHAR(255) NOT NULL, description TEXT, status VARCHAR(20) NOT NULL DEFAULT 'pending', created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(). This is a standalone schema definition — no application logic. The init script should be idempotent (CREATE TABLE IF NOT EXISTS). Satisfies AC1.
    Tests: 63/63 passed
  - [+] **React Frontend SPA** (`frontend`)
    A React + Vite + TypeScript single-page application running on port 5173 that provides the task management UI. Communicates with the backend exclusively via HTTP REST API using VITE_API_URL env var (defaulting to http://localhost:8000) (AC20).

UI features:
- Task list displaying title, colored status badge (grey=pending, blue=in_progress, green=done), and formatted created date (AC15-AC16)
- Create task form with title (required), description (optional, sends null for empty per A12), and status dropdown (AC17)
- Inline edit-in-place per task row: toggling between display mode and form mode to modify title, description, status; persists via PUT to backend (A7, AC18)
- Delete button per task row with immediate UI removal on success (AC19)
- All operations are SPA-style — no page reloads; state managed via useState/useEffect (A11)

Structure: App.tsx (root, state, effects), components/TaskList.tsx, components/TaskItem.tsx (display + inline edit toggle), components/TaskForm.tsx (create form), api.ts (typed fetch wrappers for all endpoints), types.ts (Task interface). Files kept under 300 lines (AC25). No shared code with backend (AC26).
    Tests: 79/79 passed

## Failure History

### database — implementation_bug
Component 'database' failed 0 of 2 contract tests. Since this is a leaf component, the implementation does not match the contract.
**Resolution:** Re-implement with fresh context, focusing on the failing tests.
*2026-05-04T18:41:14.837819*

### database — implementation_bug
Component 'database' failed 0 of 2 contract tests. Since this is a leaf component, the implementation does not match the contract.
**Resolution:** Re-implement with fresh context, focusing on the failing tests.
*2026-05-04T18:56:09.811143*

### database — implementation_bug
Component 'database' failed 0 of 2 contract tests. Since this is a leaf component, the implementation does not match the contract.
**Resolution:** Re-implement with fresh context, focusing on the failing tests.
*2026-05-04T19:12:37.362543*

### backend — implementation_bug
Component 'backend' failed 8 of 77 contract tests. Since this is a leaf component, the implementation does not match the contract.
**Resolution:** Re-implement with fresh context, focusing on the failing tests.
*2026-05-04T22:08:48.027263*

### frontend — implementation_bug
Component 'frontend' failed 35 of 79 contract tests. Since this is a leaf component, the implementation does not match the contract.
**Resolution:** Re-implement with fresh context, focusing on the failing tests.
*2026-05-04T22:08:48.033496*

### root — implementation_bug
The frontend component's contract_test.py file is empty or contains no valid test functions. Pytest's test collection phase finds no tests to run, resulting in a collection failure. The file exists but lacks actual test implementations for any of the frontend contract's 11 functions (fetchTasks, createTask, updateTask, deleteTask, healthCheck, resolveBaseUrl, parseErrorResponse, and the App.* handlers). Additionally, there is a module conflict between a frontend.py file and a frontend/ package directory, which may cause import resolution failures during collection.
**Resolution:** Populate contract_test.py with test functions covering the frontend contract's functions. Each test should use mocked HTTP responses (e.g., unittest.mock.patch on fetch/httpx) to validate the API wrapper behavior without requiring a live backend. Also resolve the module conflict by removing whichever of frontend.py or frontend/ package is not the canonical implementation. Finally, add a minimal pyproject.toml with [tool.pytest.ini_options] to ensure pytest can discover and collect tests correctly.
*2026-05-04T22:32:25.480546*

### root — glue_bug
The test collection fails because the integration glue layer is missing critical infrastructure: (1) no src/root/__init__.py to export the 12 contract types and 6 verification functions, (2) no src/root/root.py with a Root class wrapping verification functions with event emission, and (3) no pytest path configuration (conftest.py or pyproject.toml) to add src/backend, src/database, src/frontend, and src/root to sys.path. Without these, pytest cannot import the test modules or resolve their dependencies, causing collection to fail before any test executes.
**Resolution:** Fix in order: (1) Add pytest path configuration (conftest.py at todo-list3/ root or pyproject.toml [tool.pytest.ini_options] with pythonpath) that adds src/backend, src/database, src/frontend, src/root to sys.path. (2) Create src/root/__init__.py that defines or re-exports all 12 contract types (TaskStatus, TaskId, TaskTitle, etc.) and the 6 verification functions from glue.py. (3) Create src/root/root.py with a Root class that wraps the 6 verification functions (verify_http_api_contract, verify_cross_tier_invariants, etc.) with event emission support for emission_test.py.
*2026-05-04T22:34:22.049747*

### root — implementation_bug
The root integration component lacks its Python package implementation. There is no src/root/root/__init__.py module that defines and exports the 13 canonical types (HttpEndpoint, DatabaseURL, ValidationErrorItem, TaskStatus, TaskId, TaskTitle, OptionalString, ISOTimestamp, TaskCreateRequest, TaskUpdateRequest, TaskResponse, TaskListResponse, etc.) and 6 verify_* functions (verify_http_api_contract, verify_cross_tier_invariants, verify_schema_initialization_idempotent, verify_test_isolation, verify_cors_configuration, verify_connection_pool_lifecycle) declared in the root contract. Without this package, pytest cannot even collect the test modules (contract_test.py, emission_test.py) because their imports fail at collection time with ImportError/ModuleNotFoundError.
**Resolution:** Create the root Python package at src/root/root/__init__.py that defines or re-exports all 13 types and 6 verify_* functions from the root contract. Root-specific types (HttpEndpoint, DatabaseURL, ValidationErrorItem) need new class definitions. Also create a Root class with event_handler support for emission_test.py. Ensure PYTHONPATH includes the package path, install any missing dependencies (e.g. pydantic, httpx, psycopg2, pytest-asyncio) in the venv, and verify async test markers match installed plugins.
*2026-05-04T23:06:36.493501*

### backend — implementation_bug
Component 'backend' failed 27 of 77 contract tests. Since this is a leaf component, the implementation does not match the contract.
**Resolution:** Re-implement with fresh context, focusing on the failing tests.
*2026-05-04T23:21:46.875622*

### backend — implementation_bug
Component 'backend' failed 24 of 77 contract tests. Since this is a leaf component, the implementation does not match the contract.
**Resolution:** Re-implement with fresh context, focusing on the failing tests.
*2026-05-04T23:37:57.628118*
