# === Root (root) v1 ===
#  Dependencies: backend, database, frontend
# # Task Management Application — Root Integration Contract

Build a task management web application with a decoupled three-tier architecture: a React frontend (port 5173), a FastAPI backend (port 8000), and a PostgreSQL database (port 5432). The three components must remain separate with no shared code.

This root contract is the **integration authority**. It defines:
1. **Canonical Type Registry** — The 11 shared types that form the wire protocol between tiers.
2. **HTTP API Contract** — The six REST endpoints with exact method, path, request/response types, status codes, and error taxonomy.
3. **Cross-Tier Invariants** — Behavioral contracts that span components and must hold across the full stack.
4. **Verification Contract** — Requirements for integration testing against real PostgreSQL.

This contract exposes no implementation functions. All functions declared here are **integration verification functions** used exclusively by contract tests to assert cross-tier invariants.

# Module invariants:
#   - CROSS-TIER-01: GET /tasks returns tasks ordered by created_at DESC. This ordering is enforced by the database query (ORDER BY created_at DESC) and must be preserved through the backend serialization layer to the frontend.
#   - CROSS-TIER-02: created_at is immutable after INSERT. No UPDATE operation — whether via PUT /tasks/{id} or direct SQL — may modify created_at. The backend excludes created_at from the UPDATE SET clause, and the database trigger only modifies updated_at.
#   - CROSS-TIER-03: updated_at is refreshed on every UPDATE. The database trigger sets updated_at = NOW() BEFORE UPDATE. The backend always includes updated_at = NOW() in the UPDATE SET clause as defense-in-depth. Response updated_at >= previous updated_at.
#   - CROSS-TIER-04: DELETE /tasks/{id} is a hard delete. The row is permanently removed from the tasks table. There is no soft-delete, archival, or tombstone mechanism. Subsequent GET /tasks/{id} returns HTTP 404.
#   - CROSS-TIER-05: CORS must be enabled on the backend for the frontend origin. The backend CORS middleware must include the frontend origin (configurable, default http://localhost:5173) in Access-Control-Allow-Origin. Methods GET, POST, PUT, DELETE, OPTIONS must be allowed.
#   - CROSS-TIER-06: DATABASE_URL is the sole database configuration source. All components that connect to PostgreSQL (backend, contract tests) read connection parameters exclusively from the DATABASE_URL environment variable. No other configuration mechanism (config files, CLI args, hardcoded values) is used.
#   - CROSS-TIER-07: Connection pool lifecycle is tied to FastAPI lifespan. psycopg2.pool.ThreadedConnectionPool is initialized during FastAPI lifespan startup and closed during shutdown. No lazy initialization. No global module-level pool creation.
#   - CROSS-TIER-08: All SQL queries use parameterized placeholders (%s). No string interpolation or f-strings for user input in SQL. This invariant is absolute and applies to all database helper functions.
#   - CROSS-TIER-09: Empty or whitespace-only description strings are normalized to None/null before storage. This normalization occurs in the backend layer before the database INSERT/UPDATE. The database column allows NULL (no NOT NULL constraint).
#   - CROSS-TIER-10: All timestamps in API responses are ISO 8601 with timezone offset. No naive datetimes. No Unix timestamps. Format example: '2024-01-15T10:30:00+00:00'. Enforced by Pydantic field_serializer calling datetime.isoformat().
#   - CROSS-TIER-11: TaskStatus enum values are the same across all three tiers — {'pending', 'in_progress', 'done'}. Adding or removing a status requires coordinated changes to: (a) Python StrEnum, (b) PostgreSQL CHECK constraint, (c) TypeScript union type.
#   - CROSS-TIER-12: PUT /tasks/{id} implements PATCH semantics. Only fields present in the JSON request body (determined by Pydantic model_fields_set) are included in the SQL UPDATE SET clause. Absent fields retain their previous values. This is a deliberate deviation from strict HTTP PUT semantics.
#   - CROSS-TIER-13: Contract tests are conditionally skipped when DATABASE_URL is absent. Tests use pytest.mark.skipif or equivalent to check for the environment variable. This allows running the test suite in environments without a database.
#   - CROSS-TIER-14: Test setup/teardown manages its own test data. Tests do not depend on pre-existing database state (A10). Each test creates its required fixtures and cleans them up after execution.
#   - CROSS-TIER-15: The database init.sql script is fully idempotent. Re-execution does not fail, does not duplicate constraints or triggers, and does not modify existing data. Achieved via CREATE TABLE IF NOT EXISTS, CREATE OR REPLACE FUNCTION, and conditional trigger creation.
#   - CROSS-TIER-16: No code is shared between frontend and backend. Type definitions, validation logic, and business rules are independently implemented in each tier. The HTTP API is the sole integration boundary.
#   - CROSS-TIER-17: All source files are kept under 300 lines per operating procedure standards.
#   - CROSS-TIER-18: Title must be non-blank after whitespace stripping. Blank titles are rejected with HTTP 422 by the backend. The database allows empty string (VARCHAR NOT NULL) but the application layer prevents it.

class TaskStatus(Enum):
    """Closed set of allowed task lifecycle states; enforced by backend validation and database CHECK-equivalent logic."""
    pending = "pending"
    in_progress = "in_progress"
    done = "done"

TaskId = primitive  # Integer surrogate key for a task row, generated by PostgreSQL SERIAL.

TaskTitle = primitive  # Non-blank, whitespace-stripped task title. Leading/trailing whitespace is stripped before validation. After stripping, must have at least 1 character and at most 200 characters (frontend constraint) / 255 characters (database VARCHAR limit). The backend rejects blank-after-strip titles with HTTP 422.

OptionalString = string | None

ISOTimestamp = primitive  # A datetime with timezone info, serialized to ISO 8601 string with timezone via Pydantic field_serializer calling isoformat(). Guarantees AC14 compliance. In Python, stored as datetime.datetime; in JSON, emitted as string like '2024-01-15T10:30:00+00:00'.

class TaskCreateRequest:
    """Request body for POST /tasks — creates a new task."""
    title: string                            # required, length(1..255), Task title. Must be non-empty, max 255 characters.
    description: OptionalString = null       # optional, Optional task description. Null if omitted or empty string submitted.
    status: TaskStatus = pending             # optional, Initial task status. Defaults to 'pending' if not provided.

class TaskUpdateRequest:
    """Request body for PUT /tasks/{id} — partial update (PATCH semantics). Only provided fields are modified; created_at is never affected."""
    title: string = None                     # optional, length(1..255), New title. If provided, must be non-empty, max 255 characters.
    description: OptionalString = None       # optional, New description. Explicit null clears the field.
    status: TaskStatus = None                # optional, New status. Must be a valid TaskStatus variant.

class TaskResponse:
    """Complete task object returned by all read/write endpoints (GET, POST, PUT). Mirrors the database row with timestamps serialized as ISO 8601 strings with timezone offset."""
    id: TaskId                               # required, Auto-generated SERIAL primary key.
    title: TaskTitle                         # required, Task title, whitespace-stripped.
    description: OptionalString = null       # optional, Task description or null.
    status: TaskStatus                       # required, Current lifecycle state.
    created_at: ISOTimestamp                 # required, Creation timestamp. Immutable after INSERT.
    updated_at: ISOTimestamp                 # required, Last-modification timestamp. Set to NOW() on every UPDATE.

TaskListResponse = list[TaskResponse]
# JSON array of TaskResponse objects. Ordered by created_at DESC. May be empty if no tasks exist.

class ErrorResponse:
    """Standard error envelope returned on 404 (and other error codes) with a human-readable detail message."""
    detail: string                           # required, Human-readable error description (e.g. 'Task not found').

class ValidationErrorItem:
    """A single validation error within the 422 response. Follows Pydantic v2 validation error shape."""
    loc: list                                # required, Location path to the invalid field, e.g., ['body', 'title'].
    msg: str                                 # required, Human-readable validation error message.
    type: str                                # required, Machine-readable error type identifier, e.g., 'string_too_short', 'missing'.

class ValidationErrorResponse:
    """HTTP 422 Unprocessable Entity response body. Produced by FastAPI/Pydantic when request validation fails. This is not a custom error shape — it is FastAPI's native validation error format."""
    detail: list                             # required, Array of ValidationErrorItem objects, each describing one validation failure with loc, msg, and type fields.

class HealthResponse:
    """Response body for GET /health indicating service liveness."""
    status: string                           # required, custom(value == 'ok'), Always the literal string 'ok'.

class DeleteConfirmation:
    """Response body for DELETE /tasks/{id} on successful hard-delete (HTTP 200)."""
    detail: string                           # required, Confirmation message (e.g. 'Task deleted').
    id: TaskId                               # required, The id of the task that was deleted.

class HttpEndpoint:
    """Descriptor for one REST API endpoint in the HTTP API contract. Used for documentation and verification; not a wire type."""
    method: str                              # required, custom(value in ('GET', 'POST', 'PUT', 'DELETE')), HTTP method: GET, POST, PUT, DELETE.
    path: str                                # required, URL path pattern, e.g., '/tasks/{id}'.
    request_body_type: OptionalString = null # optional, Name of the request body type, or null if no body.
    response_body_type: str                  # required, Name of the response body type.
    success_status_code: int                 # required, HTTP status code on success.
    content_type: str                        # required, Content-Type header for request and response.

DatabaseURL = primitive  # PostgreSQL connection string read from DATABASE_URL environment variable. Must be a valid PostgreSQL URI (e.g., 'postgresql://user:pass@host:5432/dbname'). This is the sole database configuration source across all tiers.

class string:
    """Auto-stubbed type — referenced but not defined in contract 'root'"""
    pass

async def verify_http_api_contract(
    backend_base_url: str,     # regex(^https?://)
) -> bool:
    """
    Integration verification function. Validates that the backend exposes all six REST endpoints with the correct method, path, request/response types, and status codes. The canonical endpoint table is:

| # | Method | Path          | Request Body       | Response Body        | Success Status |
|---|--------|---------------|--------------------|----------------------|----------------|
| 1 | GET    | /health       | —                  | HealthResponse       | 200            |
| 2 | GET    | /tasks        | —                  | TaskListResponse     | 200            |
| 3 | POST   | /tasks        | TaskCreateRequest  | TaskResponse         | 201            |
| 4 | GET    | /tasks/{id}   | —                  | TaskResponse         | 200            |
| 5 | PUT    | /tasks/{id}   | TaskUpdateRequest  | TaskResponse         | 200            |
| 6 | DELETE | /tasks/{id}   | —                  | DeleteConfirmation   | 200            |

All endpoints accept and return Content-Type: application/json.

PUT /tasks/{id} implements PATCH semantics: only fields present in the JSON body (tracked by Pydantic model_fields_set) are updated. This is a deliberate deviation from strict PUT semantics.

Error taxonomy:
- 404 → ErrorResponse {detail: 'Task not found'}
- 422 → ValidationErrorResponse {detail: [...ValidationErrorItem]}
- 500 → ErrorResponse {detail: 'Database connection error'}

    Preconditions:
      - Backend FastAPI application is running and reachable at backend_base_url
      - PostgreSQL database is initialized with tasks table via init.sql
      - DATABASE_URL environment variable is set for the backend process

    Postconditions:
      - Returns true if all six endpoints respond with correct status codes and response shapes
      - No persistent side effects — any tasks created during verification are cleaned up

    Errors:
      - backend_unreachable (ConnectionError): Backend is not running or not reachable at the given base URL
      - endpoint_mismatch (AssertionError): An endpoint returns an unexpected status code or response shape

    Side effects: none
    Idempotent: yes
    """
    ...

async def verify_cross_tier_invariants(
    backend_base_url: str,
    database_url: str,
) -> bool:
    """
    Integration verification function. Validates the cross-tier behavioral invariants that must hold across the full stack:

(a) TaskList ordering: GET /tasks returns tasks ordered by created_at DESC.
(b) created_at immutability: PUT /tasks/{id} never modifies created_at.
(c) updated_at refresh: PUT /tasks/{id} always sets updated_at >= previous updated_at.
(d) Hard delete: DELETE /tasks/{id} permanently removes the row; subsequent GET /tasks/{id} returns 404.
(e) Description normalization: Empty or whitespace-only description in POST /tasks is stored as null (A12).
(f) Title stripping: Leading/trailing whitespace on title is stripped before storage.
(g) Status default: POST /tasks without status field defaults to 'pending'.
(h) Timestamp format: All timestamps in responses are ISO 8601 with timezone offset (AC14).

    Preconditions:
      - Backend FastAPI application is running at backend_base_url
      - PostgreSQL database is initialized and accessible via database_url
      - tasks table exists with correct schema

    Postconditions:
      - Returns true if all cross-tier invariants hold
      - Test data created during verification is cleaned up (transaction rollback or explicit DELETE)

    Errors:
      - backend_unreachable (ConnectionError): Backend is not running or not reachable
      - database_unreachable (ConnectionError): PostgreSQL is not running or not reachable via database_url
      - invariant_violation (AssertionError): One or more cross-tier invariants do not hold

    Side effects: none
    Idempotent: yes
    """
    ...

def verify_schema_initialization_idempotent(
    database_url: str,         # regex(^postgresql://)
) -> bool:
    """
    Integration verification function. Validates that the database init.sql script is fully idempotent: executing it twice produces no errors and does not modify existing data. Verifies that the tasks table exists with the correct six columns, the CHECK constraint on status is present, and the update_updated_at_column trigger is attached.

    Preconditions:
      - PostgreSQL server is running and accepting connections
      - database_url contains valid credentials with CREATE TABLE, CREATE FUNCTION, CREATE TRIGGER privileges

    Postconditions:
      - Returns true if init.sql can be executed twice without error
      - tasks table exists with columns: id (SERIAL PK), title (VARCHAR(255) NOT NULL), description (TEXT nullable), status (VARCHAR(20) NOT NULL DEFAULT 'pending'), created_at (TIMESTAMPTZ NOT NULL DEFAULT NOW()), updated_at (TIMESTAMPTZ NOT NULL DEFAULT NOW())
      - CHECK constraint enforces status IN ('pending', 'in_progress', 'done')
      - Trigger update_updated_at_column fires BEFORE UPDATE on tasks table
      - Pre-existing data in tasks table is not modified by re-execution

    Errors:
      - database_unreachable (ConnectionError): PostgreSQL is not running or connection refused
      - schema_mismatch (AssertionError): Table structure does not match expected schema after init.sql execution
      - idempotency_failure (AssertionError): Second execution of init.sql raises an error

    Side effects: none
    Idempotent: yes
    """
    ...

def verify_test_isolation(
    database_url: str,
) -> bool:
    """
    Integration verification function. Validates that contract tests properly isolate test data: (a) Tests do not depend on pre-existing database state (A10). (b) Test setup/teardown manages its own data via explicit INSERT/DELETE or transaction rollback. (c) Contract tests are conditionally skipped when DATABASE_URL is absent. (d) Each test run leaves the database in its pre-test state (no leaked rows).

    Preconditions:
      - PostgreSQL is accessible via database_url
      - tasks table exists

    Postconditions:
      - Returns true if test isolation properties hold
      - The tasks table row count is unchanged after verification

    Errors:
      - database_unreachable (ConnectionError): PostgreSQL is not running or connection refused
      - isolation_violation (AssertionError): Test data leaked into the database or pre-existing data was modified

    Side effects: none
    Idempotent: yes
    """
    ...

async def verify_cors_configuration(
    backend_base_url: str,
    frontend_origin: str,
) -> bool:
    """
    Integration verification function. Validates that the backend CORS middleware is configured to allow the frontend origin (http://localhost:5173 or configurable). Sends an OPTIONS preflight request and verifies Access-Control-Allow-Origin, Access-Control-Allow-Methods, and Access-Control-Allow-Headers response headers.

    Preconditions:
      - Backend FastAPI application is running at backend_base_url

    Postconditions:
      - Returns true if CORS headers permit the frontend origin
      - Access-Control-Allow-Origin includes the frontend_origin or '*'
      - Access-Control-Allow-Methods includes GET, POST, PUT, DELETE, OPTIONS
      - Access-Control-Allow-Headers includes Content-Type

    Errors:
      - backend_unreachable (ConnectionError): Backend is not running or not reachable
      - cors_not_configured (AssertionError): CORS headers are missing or do not allow the frontend origin

    Side effects: none
    Idempotent: yes
    """
    ...

async def verify_connection_pool_lifecycle(
    backend_base_url: str,
) -> bool:
    """
    Integration verification function. Validates that the psycopg2 ThreadedConnectionPool lifecycle is correctly tied to FastAPI lifespan: (a) Pool is initialized on application startup. (b) Pool is closed on application shutdown. (c) Database queries work during application runtime. (d) Pool exhaustion returns a meaningful error (HTTP 500) rather than hanging.

    Preconditions:
      - Backend FastAPI application is running at backend_base_url
      - PostgreSQL database is running and accessible

    Postconditions:
      - Returns true if connection pool is functional (GET /tasks succeeds)
      - Database queries execute without connection errors during application runtime

    Errors:
      - backend_unreachable (ConnectionError): Backend is not running or not reachable
      - pool_not_initialized (AssertionError): Database queries fail because the connection pool was not initialized on startup

    Side effects: none
    Idempotent: yes
    """
    ...

# ── REQUIRED EXPORTS ──────────────────────────────────
# Your implementation module MUST export ALL of these names
# with EXACTLY these spellings. Tests import them by name.
# __all__ = ['TaskStatus', 'OptionalString', 'TaskCreateRequest', 'TaskUpdateRequest', 'TaskResponse', 'TaskListResponse', 'ErrorResponse', 'ValidationErrorItem', 'ValidationErrorResponse', 'HealthResponse', 'DeleteConfirmation', 'HttpEndpoint', 'string', 'verify_http_api_contract', 'ConnectionError', 'AssertionError', 'verify_cross_tier_invariants', 'verify_schema_initialization_idempotent', 'verify_test_isolation', 'verify_cors_configuration', 'verify_connection_pool_lifecycle']
