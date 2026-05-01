# === Main (root) v1 ===
# Root interface contract for a personal task management web app. Defines canonical types (frozen dataclasses), REST endpoint contracts, and pure validation functions for a React/Express/PostgreSQL stack. All types use Python 3.12+ stdlib dataclasses (frozen=True, slots=True, kw_only=True). JSON Merge Patch semantics (RFC 7396) for PATCH: absent key = unchanged, explicit null = clear field. No envelope wrappers — response bodies are bare types. Serialization: snake_case keys, lowercase hyphenated UUIDs, ISO 8601 timestamps with Z suffix, YYYY-MM-DD dates, integer priority.

# Module invariants:
#   - All Task instances are immutable (frozen dataclasses). Mutation requires creating a new instance.
#   - Task.id is a UUID v4, generated server-side, and is unique across all tasks.
#   - Task.title is never empty or whitespace-only after validation. Max 500 characters.
#   - Task.priority is always >= 1.
#   - Task.created_at is always a valid UTC timestamp and is immutable after creation.
#   - Task.due_date is either a valid YYYY-MM-DD date string or None.
#   - All JSON serialization uses snake_case keys with no envelope wrapper.
#   - UUID strings are always lowercase hyphenated (8-4-4-4-12).
#   - Timestamps are always ISO 8601 with Z suffix (UTC).
#   - PATCH semantics follow RFC 7396 JSON Merge Patch: absent = unchanged, null = clear (for nullable fields).
#   - The Sentinel.UNSET value is used only in UpdateTaskRequest to distinguish absent from null; it never appears in serialized JSON or in Task instances.
#   - validate_create_task and validate_update_task are pure functions with no side effects.
#   - HTTP 201 is used only for POST /tasks success. All other successes use HTTP 200.
#   - HTTP 400 is returned only for validation errors. HTTP 404 is returned only when a task_id does not match any existing row.
#   - DELETE /tasks/:id returns the deleted Task snapshot (HTTP 200), not an empty body.
#   - The tasks table has indexes on priority and due_date columns for future query optimization.
#   - The backend is the single source of truth — no client-side caching of authoritative state.

TaskUUID = primitive  # A UUID v4 string in lowercase hyphenated form (8-4-4-4-12). Used as the primary key for task records.

TaskTitle = primitive  # A non-empty, whitespace-stripped task title. Max 500 characters after stripping.

Priority = primitive  # An integer representing task priority (1 = default/lowest, higher = more urgent).

DateString = primitive  # An ISO 8601 date string in YYYY-MM-DD format (no time component).

TimestampTZ = primitive  # An ISO 8601 timestamp string with timezone (e.g. 2024-01-15T10:30:00.000Z).

OptionalDateString = Any | None

class HttpStatusCode(Enum):
    """The set of HTTP status codes used across the API for consistent response handling."""
    200 = "200"
    201 = "201"
    400 = "400"
    404 = "404"

class Task:
    """The canonical task entity shared across database, backend API, and frontend display."""
    id: UUID                                 # required, Unique identifier for the task, generated server-side as a v4 UUID.
    title: string                            # required, length(min=1), The task title; must be a non-empty string.
    completed: boolean                       # required, Whether the task has been marked as complete.
    priority: Priority                       # required, range(min=1), Task priority level; defaults to 1.
    due_date: OptionalDateString = null      # optional, Optional due date for the task in YYYY-MM-DD format.
    created_at: TimestampTZ                  # required, Server-generated timestamp of when the task was created.

TaskList = list[Task]
# An ordered list of Task objects returned by the GET /tasks endpoint.

class CreateTaskRequest:
    """Request body for POST /tasks — only title is required; other fields are optional overrides."""
    title: string                            # required, length(min=1), The title for the new task; must be a non-empty string.
    priority: Priority = 1                   # optional, range(min=1), Optional priority override; defaults to 1 if omitted.
    due_date: OptionalDateString = null      # optional, Optional due date in YYYY-MM-DD format.

class UpdateTaskRequest:
    """Request body for PATCH /tasks/:id — all fields are optional; only provided fields are updated."""
    title: string = None                     # optional, length(min=1), New title for the task; must be non-empty if provided.
    completed: boolean = None                # optional, New completion status for the task.
    priority: Priority = None                # optional, range(min=1), New priority level for the task.
    due_date: OptionalDateString = None      # optional, New due date; set to null to clear, or a YYYY-MM-DD string to set.

class ApiErrorResponse:
    """Standard error response body returned by the API for 400 and 404 responses."""
    status: HttpStatusCode                   # required, The HTTP status code of the error (e.g. 400, 404).
    error: string                            # required, A human-readable error message describing what went wrong.

class EndpointContract:
    """Describes a single REST endpoint contract: HTTP method, path pattern, request type, and mapping of status codes to response types. Used in contracts.py to define exhaustive endpoint specifications."""
    method: str                              # required, custom(method in ('GET', 'POST', 'PATCH', 'DELETE')), HTTP method: GET, POST, PATCH, DELETE.
    path: str                                # required, regex(^/tasks(/:id)?$), URL path pattern, e.g. '/tasks' or '/tasks/:id'.
    request_type: str                        # required, Name of the request body type, or 'None' if no body.
    success_status: HttpStatusCode           # required, HTTP status code on success.
    success_response_type: str               # required, Name of the response type on success.
    error_branches: list                     # required, List of (HttpStatusCode, ApiErrorResponse) error branch specifications.

ValidationResult = CreateTaskRequest | UpdateTaskRequest | str

class Sentinel(Enum):
    """Sentinel enum with a single UNSET member. Used in UpdateTaskRequest to distinguish absent fields from explicitly-set fields (including null). Needed for due_date where null means 'clear the due date' vs absent means 'do not change'."""
    UNSET = "UNSET"

UUID = primitive  # A v4 UUID string uniquely identifying a task.

class boolean:
    """Auto-stubbed type — referenced but not defined in contract 'root'"""
    pass

class string:
    """Auto-stubbed type — referenced but not defined in contract 'root'"""
    pass

def validate_create_task(
    request: CreateTaskRequest,
) -> ValidationResult:
    """
    Pure validation function for CreateTaskRequest. Strips whitespace from title, rejects empty titles, validates priority >= 1, validates due_date format (YYYY-MM-DD) if provided. Returns either a validated CreateTaskRequest with stripped title or an error string describing the first validation failure. Defined in validators.py.

    Preconditions:
      - request is a CreateTaskRequest instance

    Postconditions:
      - On success: returned CreateTaskRequest has title == request.title.strip() and len(title) >= 1 and len(title) <= 500
      - On success: returned CreateTaskRequest has priority >= 1
      - On success: if due_date is not null, it is a valid YYYY-MM-DD date string
      - On error: returned str is a non-empty human-readable error message

    Errors:
      - empty_title (str): request.title is None, not a string, or empty/whitespace-only after stripping
          example: Title is required and must not be empty.
      - title_too_long (str): request.title.strip() exceeds 500 characters
          example: Title must not exceed 500 characters.
      - invalid_priority (str): request.priority is not an integer or is < 1
          example: Priority must be a positive integer >= 1.
      - invalid_due_date (str): request.due_date is provided but does not match YYYY-MM-DD or is not a valid calendar date
          example: Due date must be a valid date in YYYY-MM-DD format.

    Side effects: none
    Idempotent: yes
    """
    ...

def validate_update_task(
    request: UpdateTaskRequest,
) -> ValidationResult:
    """
    Pure validation function for UpdateTaskRequest. For each field that is not UNSET: strips and validates title (non-empty, <= 500 chars), validates priority >= 1, validates due_date format (YYYY-MM-DD) or null. Returns either a validated UpdateTaskRequest or an error string. At least one field must be non-UNSET. Defined in validators.py.

    Preconditions:
      - request is an UpdateTaskRequest instance

    Postconditions:
      - On success: at least one field in the returned UpdateTaskRequest is not UNSET
      - On success: if title is not UNSET, it equals request.title.strip() and len >= 1 and len <= 500
      - On success: if priority is not UNSET, it is >= 1
      - On success: if due_date is not UNSET and not None, it is a valid YYYY-MM-DD date string
      - On success: if completed is not UNSET, it is a bool
      - On error: returned str is a non-empty human-readable error message

    Errors:
      - no_fields_provided (str): All fields in the request are UNSET (empty patch body)
          example: At least one field must be provided for update.
      - empty_title (str): title is provided but is empty/whitespace-only after stripping
          example: Title must not be empty.
      - title_too_long (str): title is provided and exceeds 500 characters after stripping
          example: Title must not exceed 500 characters.
      - invalid_priority (str): priority is provided but is not an integer or is < 1
          example: Priority must be a positive integer >= 1.
      - invalid_due_date (str): due_date is provided (not UNSET, not null) but does not match YYYY-MM-DD or is not a valid calendar date
          example: Due date must be a valid date in YYYY-MM-DD format.
      - invalid_completed (str): completed is provided but is not a boolean
          example: Completed must be a boolean.

    Side effects: none
    Idempotent: yes
    """
    ...

async def create_task(
    request: CreateTaskRequest,
) -> Task:
    """
    POST /tasks — Creates a new task. Validates the request body, generates a UUID v4 id and created_at timestamp server-side, inserts into PostgreSQL, and returns the created Task with HTTP 201. Returns HTTP 400 with ApiErrorResponse if validation fails.

    Preconditions:
      - request has been deserialized from a valid JSON object

    Postconditions:
      - On 201: returned Task.id is a valid UUID v4
      - On 201: returned Task.title == request.title.strip()
      - On 201: returned Task.completed == false
      - On 201: returned Task.priority == request.priority (or 1 if not provided)
      - On 201: returned Task.due_date == validated request.due_date (or null if not provided)
      - On 201: returned Task.created_at is a valid UTC timestamp at or after the time the request was received
      - On 201: a row with the returned Task's id exists in the tasks table

    Errors:
      - validation_error (ApiErrorResponse): validate_create_task returns an error string (empty title, invalid priority, invalid due_date)
          status: 400
          error: VALIDATION_ERROR

    Side effects: Inserts a row into the PostgreSQL tasks table
    Idempotent: no
    """
    ...

async def list_tasks() -> TaskList:
    """
    GET /tasks — Returns all tasks as a JSON array (TaskList). No pagination in this single-user app. Returns HTTP 200 with an empty array if no tasks exist.

    Postconditions:
      - Returned list contains exactly the set of tasks currently in the tasks table
      - Each element in the returned list is a valid Task
      - HTTP status is always 200

    Side effects: Reads all rows from the PostgreSQL tasks table
    Idempotent: yes
    """
    ...

async def get_task(
    task_id: TaskUUID,
) -> Task:
    """
    GET /tasks/:id — Returns a single task by UUID. Returns HTTP 200 with the Task if found, HTTP 404 with ApiErrorResponse if not found.

    Preconditions:
      - task_id is a valid UUID v4 string

    Postconditions:
      - On 200: returned Task.id == task_id
      - On 200: returned Task matches the current state of the row in the tasks table
      - On 404: returned ApiErrorResponse.error == 'NOT_FOUND'

    Errors:
      - task_not_found (ApiErrorResponse): No row exists in the tasks table with the given task_id
          status: 404
          error: NOT_FOUND
          message: Task not found.

    Side effects: Reads a row from the PostgreSQL tasks table
    Idempotent: yes
    """
    ...

async def update_task(
    task_id: TaskUUID,
    request: UpdateTaskRequest,
) -> Task:
    """
    PATCH /tasks/:id — Updates a task using JSON Merge Patch semantics (RFC 7396). Only fields present in the request body are updated; absent fields are unchanged. Explicit null on due_date clears it. Returns HTTP 200 with the full updated Task. Returns HTTP 404 if not found, HTTP 400 if validation fails.

    Preconditions:
      - task_id is a valid UUID v4 string
      - request has been deserialized from a valid JSON object with UNSET sentinels applied for absent keys

    Postconditions:
      - On 200: returned Task.id == task_id
      - On 200: for each field in request that is not UNSET, the returned Task reflects the new value
      - On 200: for each field in request that is UNSET, the returned Task retains the previous value
      - On 200: returned Task.created_at is unchanged from the original
      - On 200: the tasks table row has been updated to match the returned Task
      - On 404: returned ApiErrorResponse.error == 'NOT_FOUND'
      - On 400: returned ApiErrorResponse.error == 'VALIDATION_ERROR'

    Errors:
      - task_not_found (ApiErrorResponse): No row exists in the tasks table with the given task_id
          status: 404
          error: NOT_FOUND
          message: Task not found.
      - validation_error (ApiErrorResponse): validate_update_task returns an error string (empty title, invalid priority, invalid due_date, no fields, invalid completed)
          status: 400
          error: VALIDATION_ERROR

    Side effects: Updates a row in the PostgreSQL tasks table
    Idempotent: yes
    """
    ...

async def delete_task(
    task_id: TaskUUID,
) -> Task:
    """
    DELETE /tasks/:id — Deletes a task by UUID. Returns HTTP 200 with the deleted Task object (snapshot before deletion). Returns HTTP 404 with ApiErrorResponse if not found.

    Preconditions:
      - task_id is a valid UUID v4 string

    Postconditions:
      - On 200: returned Task.id == task_id
      - On 200: returned Task is the state of the task immediately before deletion
      - On 200: no row with the given task_id exists in the tasks table after the call
      - On 404: returned ApiErrorResponse.error == 'NOT_FOUND'
      - On 404: the tasks table is unchanged

    Errors:
      - task_not_found (ApiErrorResponse): No row exists in the tasks table with the given task_id
          status: 404
          error: NOT_FOUND
          message: Task not found.

    Side effects: Deletes a row from the PostgreSQL tasks table
    Idempotent: no
    """
    ...

def get_endpoint_contracts() -> list:
    """
    Returns the exhaustive list of EndpointContract definitions for all 5 REST endpoints. Used in contracts.py for endpoint contract specification and in test_contracts.py for exhaustiveness assertions. Pure function, returns a static list.

    Postconditions:
      - Returned list contains exactly 5 EndpointContract objects
      - Endpoints covered: POST /tasks, GET /tasks, GET /tasks/:id, PATCH /tasks/:id, DELETE /tasks/:id
      - Every HttpStatusCode variant used in the API appears in at least one contract
      - Every error branch maps to ApiErrorResponse

    Side effects: none
    Idempotent: yes
    """
    ...

def task_to_dict(
    task: Task,
) -> dict:
    """
    Serializes a Task to a JSON-compatible dict with snake_case keys. UUID as lowercase hyphenated string, timestamps as ISO 8601 with Z, dates as YYYY-MM-DD, priority as integer, due_date as string or null. No envelope wrapper. Defined in types.py for serialization round-trip support.

    Preconditions:
      - task is a valid Task instance

    Postconditions:
      - Returned dict has exactly the keys: id, title, completed, priority, due_date, created_at
      - All keys are snake_case strings
      - dict['id'] is a lowercase hyphenated UUID string
      - dict['created_at'] is an ISO 8601 string ending in Z
      - dict['due_date'] is a YYYY-MM-DD string or None
      - dict['priority'] is an int >= 1
      - dict['completed'] is a bool

    Side effects: none
    Idempotent: yes
    """
    ...

def task_from_dict(
    data: dict,
) -> Task:
    """
    Deserializes a dict (e.g., from JSON or a database row mapping) into a Task instance. Validates all fields. Defined in types.py for serialization round-trip support.

    Preconditions:
      - data is a dict with string keys

    Postconditions:
      - Returned Task has all fields populated from the dict
      - task_to_dict(task_from_dict(data)) == data (round-trip identity for well-formed input)

    Errors:
      - missing_required_field (str): A required field (id, title, created_at) is missing from the dict
          example: Missing required field: title
      - invalid_field_value (str): A field value fails its type validator (e.g., invalid UUID, empty title, priority < 1)
          example: Invalid value for field 'priority': must be >= 1

    Side effects: none
    Idempotent: yes
    """
    ...

# ── REQUIRED EXPORTS ──────────────────────────────────
# Your implementation module MUST export ALL of these names
# with EXACTLY these spellings. Tests import them by name.
# __all__ = ['OptionalDateString', 'HttpStatusCode', 'Task', 'TaskList', 'CreateTaskRequest', 'UpdateTaskRequest', 'ApiErrorResponse', 'EndpointContract', 'ValidationResult', 'Sentinel', 'boolean', 'string', 'validate_create_task', 'validate_update_task', 'create_task', 'list_tasks', 'get_task', 'update_task', 'delete_task', 'get_endpoint_contracts', 'task_to_dict', 'task_from_dict']
