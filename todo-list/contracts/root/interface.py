# === Main (root) v1 ===
# Todo List web application with a FastAPI backend, PostgreSQL database (via psycopg2 raw SQL), and a single-page vanilla JavaScript frontend. Serves 5 HTTP endpoints for CRUD operations on tasks and a static HTML file. No ORM, no authentication, no pagination. Single Python source file (src/root/main.py) plus a static frontend (src/root/static/index.html).

# Module invariants:
#   - All SQL queries use parameterized placeholders (%s) — no string interpolation or f-string SQL construction.
#   - All INSERT and UPDATE statements use RETURNING to retrieve the full row, avoiding a separate SELECT.
#   - The tasks table schema is immutable after init_db: id SERIAL PRIMARY KEY, title VARCHAR(500) NOT NULL, completed BOOLEAN NOT NULL DEFAULT FALSE, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW().
#   - RealDictCursor is used for all cursor operations so rows are returned as dicts keyed by column name.
#   - No ORM is used; all database interaction is via raw SQL through psycopg2.
#   - The backend is a single Python file: src/root/main.py.
#   - The frontend is a single HTML file with inline CSS and JS: src/root/static/index.html.
#   - No authentication or authorization is applied to any endpoint.
#   - No pagination is applied to GET /tasks; all matching rows are returned.
#   - Error responses conform to the {"detail": "message"} JSON structure.
#   - DELETE /tasks/{id} returns exactly 204 with an empty body on success, never a JSON body.
#   - POST /tasks returns exactly 201 on success.
#   - The DATABASE_URL environment variable must be set before the application starts.

TaskId = primitive  # An integer identifier for a task, corresponding to the SERIAL PRIMARY KEY in the database.

TaskTitle = primitive  # Non-empty string of at most 500 characters representing a task's title. Maps to VARCHAR(500) NOT NULL in the database.

class Task:
    """A complete task object as stored in the database and returned by the API."""
    id: TaskId                               # required, Unique auto-incrementing identifier for the task.
    title: String                            # required, length(1..500), The title/description of the task. Max 500 characters.
    completed: Bool                          # required, Whether the task has been completed. Defaults to false.
    created_at: DateTime                     # required, Timestamp when the task was created, with timezone.

class CreateTaskRequest:
    """Request body for POST /tasks to create a new task."""
    title: String                            # required, length(1..500), The title of the task to create. Max 500 characters.

class UpdateTaskRequest:
    """Request body for PATCH /tasks/{id} to update task completion status."""
    completed: Bool                          # required, The new completion status for the task.

class ErrorResponse:
    """Standard JSON error response returned by the API for error conditions (e.g. 404)."""
    detail: String                           # required, Human-readable error message describing what went wrong.

TaskList = list[Task]
# An ordered list of Task objects returned by the GET /tasks endpoint.

CompletedFilter = bool | None

DatabaseURL = primitive  # PostgreSQL connection string read from the DATABASE_URL environment variable. Must be a valid postgresql:// URI.

String = primitive  # A UTF-8 string value.

Bool = primitive  # A boolean true/false value.

DateTime = primitive  # An ISO-8601 timestamp string with timezone (e.g. '2024-01-15T10:30:00+00:00').

def init_db(
    database_url: DatabaseURL,
) -> None:
    """
    Establishes a connection to PostgreSQL using DATABASE_URL and executes CREATE TABLE IF NOT EXISTS to ensure the tasks table exists with the required schema (id SERIAL PRIMARY KEY, title VARCHAR(500) NOT NULL, completed BOOLEAN NOT NULL DEFAULT FALSE, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()). Called once at application startup.

    Preconditions:
      - DATABASE_URL environment variable is set and contains a valid PostgreSQL connection string.
      - The PostgreSQL server at the specified URL is reachable and accepting connections.

    Postconditions:
      - The 'tasks' table exists in the connected database with columns: id (SERIAL PK), title (VARCHAR(500) NOT NULL), completed (BOOLEAN NOT NULL DEFAULT FALSE), created_at (TIMESTAMPTZ NOT NULL DEFAULT NOW()).
      - A reusable database connection or connection factory is available for subsequent operations.

    Errors:
      - missing_database_url (RuntimeError): DATABASE_URL environment variable is not set or is empty.
          detail: DATABASE_URL environment variable is not set.
      - connection_failed (psycopg2.OperationalError): Cannot connect to PostgreSQL at the specified URL (network error, auth failure, database does not exist).
          detail: Failed to connect to database.

    Side effects: none
    Idempotent: yes
    """
    ...

def get_db_connection() -> any:
    """
    Returns a psycopg2 connection object connected to the PostgreSQL database specified by DATABASE_URL. Used as a FastAPI dependency or utility to obtain a connection for each request. The connection uses RealDictCursor for dict-based row access.

    Preconditions:
      - init_db has been called successfully at least once.
      - DATABASE_URL is set and the database is reachable.

    Postconditions:
      - Returns an open psycopg2 connection configured with RealDictCursor cursor factory.
      - The connection is in autocommit mode or the caller is responsible for commit/rollback.

    Errors:
      - connection_failed (psycopg2.OperationalError): PostgreSQL is unreachable or the connection pool is exhausted.
          detail: Database connection unavailable.

    Side effects: none
    Idempotent: yes
    """
    ...

def create_task(
    title: TaskTitle,
) -> Task:
    """
    Inserts a new task row into the tasks table with the given title, completed=FALSE, and created_at=NOW(). Uses INSERT ... RETURNING to retrieve the full row. Returns the created Task.

    Preconditions:
      - A valid database connection is available.
      - title is a non-empty string of at most 500 characters.

    Postconditions:
      - A new row exists in the tasks table with the given title, completed=FALSE, and a server-generated id and created_at.
      - The returned Task object contains the exact values stored in the database.

    Errors:
      - database_error (psycopg2.Error): The INSERT query fails due to a database error (connection lost, constraint violation).
          detail: Failed to create task.

    Side effects: none
    Idempotent: no
    """
    ...

def list_tasks(
    completed: CompletedFilter = None,
) -> TaskList:
    """
    Queries the tasks table and returns all tasks, optionally filtered by completion status. If completed is None, returns all rows. If completed is True or False, adds a WHERE completed = %s clause. Returns rows ordered by created_at or id (implementation choice).

    Preconditions:
      - A valid database connection is available.

    Postconditions:
      - Returns a list of Task objects matching the filter criteria.
      - If completed is None, all rows in the tasks table are returned.
      - If completed is True, only rows where completed=TRUE are returned.
      - If completed is False, only rows where completed=FALSE are returned.
      - The returned list may be empty if no tasks match.

    Errors:
      - database_error (psycopg2.Error): The SELECT query fails due to a database error.
          detail: Failed to list tasks.

    Side effects: none
    Idempotent: yes
    """
    ...

def update_task(
    task_id: TaskId,
    completed: bool,
) -> Task:
    """
    Updates the completed field of an existing task identified by id. Uses UPDATE ... WHERE id = %s RETURNING to retrieve the updated row. Returns the updated Task or None if the task does not exist.

    Preconditions:
      - A valid database connection is available.
      - task_id is a positive integer.

    Postconditions:
      - If a task with the given id exists, its completed field is updated to the new value and the updated row is returned.
      - If no task with the given id exists, returns None (caller is responsible for raising 404).
      - The title, id, and created_at fields of the task are unchanged.

    Errors:
      - task_not_found (ValueError): No task with the given id exists in the tasks table.
          detail: Task not found
      - database_error (psycopg2.Error): The UPDATE query fails due to a database error.
          detail: Failed to update task.

    Side effects: none
    Idempotent: yes
    """
    ...

def delete_task(
    task_id: TaskId,
) -> bool:
    """
    Deletes a task row identified by id from the tasks table. Returns True if a row was deleted, False if no row with that id existed.

    Preconditions:
      - A valid database connection is available.
      - task_id is a positive integer.

    Postconditions:
      - If a task with the given id existed, it is removed from the tasks table and True is returned.
      - If no task with the given id existed, no rows are affected and False is returned.

    Errors:
      - task_not_found (ValueError): No task with the given id exists in the tasks table.
          detail: Task not found
      - database_error (psycopg2.Error): The DELETE query fails due to a database error.
          detail: Failed to delete task.

    Side effects: none
    Idempotent: yes
    """
    ...

def handle_serve_index() -> any:
    """
    FastAPI route handler for GET /. Serves the static/index.html file as a FileResponse. Returns 200 with text/html content type.

    Preconditions:
      - The file static/index.html exists relative to the application root.

    Postconditions:
      - Returns a FileResponse with the contents of static/index.html and content type text/html.

    Errors:
      - file_not_found (HTTPException): The static/index.html file does not exist on disk.
          status_code: 500
          detail: Frontend file not found.

    Side effects: none
    Idempotent: yes
    """
    ...

def handle_create_task(
    body: CreateTaskRequest,
) -> Task:
    """
    FastAPI route handler for POST /tasks. Accepts a CreateTaskRequest JSON body, calls create_task, and returns the created Task with HTTP 201 status.

    Preconditions:
      - Request body is valid JSON conforming to CreateTaskRequest schema.
      - Database connection is available.

    Postconditions:
      - A new task is persisted in the database.
      - Response status is 201 Created.
      - Response body is the created Task as JSON.

    Errors:
      - validation_error (HTTPException): Request body is missing, malformed, or title fails validation (empty or > 500 chars).
          status_code: 422
          detail: Validation error
      - database_error (HTTPException): Database INSERT fails.
          status_code: 500
          detail: Internal server error.

    Side effects: none
    Idempotent: no
    """
    ...

def handle_list_tasks(
    completed: CompletedFilter = None,
) -> TaskList:
    """
    FastAPI route handler for GET /tasks. Accepts an optional 'completed' query parameter (bool or None). Calls list_tasks and returns the TaskList with HTTP 200 status.

    Preconditions:
      - Database connection is available.

    Postconditions:
      - Response status is 200 OK.
      - Response body is a JSON array of Task objects matching the filter.

    Errors:
      - database_error (HTTPException): Database SELECT fails.
          status_code: 500
          detail: Internal server error.

    Side effects: none
    Idempotent: yes
    """
    ...

def handle_update_task(
    task_id: TaskId,
    body: UpdateTaskRequest,
) -> Task:
    """
    FastAPI route handler for PATCH /tasks/{id}. Accepts a TaskId path parameter and an UpdateTaskRequest JSON body. Calls update_task and returns the updated Task with HTTP 200 status, or raises 404 if the task does not exist.

    Preconditions:
      - task_id is a positive integer.
      - Request body is valid JSON conforming to UpdateTaskRequest schema.
      - Database connection is available.

    Postconditions:
      - If the task exists, its completed field is updated and the full updated Task is returned with status 200.
      - If the task does not exist, an ErrorResponse with status 404 and detail 'Task not found' is returned.

    Errors:
      - task_not_found (HTTPException): No task with the given id exists.
          status_code: 404
          detail: Task not found
      - validation_error (HTTPException): Request body is missing, malformed, or id path param is not a valid integer.
          status_code: 422
          detail: Validation error
      - database_error (HTTPException): Database UPDATE fails.
          status_code: 500
          detail: Internal server error.

    Side effects: none
    Idempotent: yes
    """
    ...

def handle_delete_task(
    task_id: TaskId,
) -> None:
    """
    FastAPI route handler for DELETE /tasks/{id}. Accepts a TaskId path parameter. Calls delete_task and returns HTTP 204 No Content on success, or raises 404 if the task does not exist.

    Preconditions:
      - task_id is a positive integer.
      - Database connection is available.

    Postconditions:
      - If the task existed, it is removed from the database and a 204 No Content response is returned with an empty body.
      - If the task did not exist, an ErrorResponse with status 404 and detail 'Task not found' is returned.

    Errors:
      - task_not_found (HTTPException): No task with the given id exists.
          status_code: 404
          detail: Task not found
      - validation_error (HTTPException): id path param is not a valid positive integer.
          status_code: 422
          detail: Validation error
      - database_error (HTTPException): Database DELETE fails.
          status_code: 500
          detail: Internal server error.

    Side effects: none
    Idempotent: yes
    """
    ...

# ── REQUIRED EXPORTS ──────────────────────────────────
# Your implementation module MUST export ALL of these names
# with EXACTLY these spellings. Tests import them by name.
# __all__ = ['Task', 'CreateTaskRequest', 'UpdateTaskRequest', 'ErrorResponse', 'TaskList', 'CompletedFilter', 'init_db', 'get_db_connection', 'create_task', 'list_tasks', 'update_task', 'delete_task', 'handle_serve_index', 'HTTPException', 'handle_create_task', 'handle_list_tasks', 'handle_update_task', 'handle_delete_task']
